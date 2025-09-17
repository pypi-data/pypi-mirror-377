# Copyright 2023- Gimlet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
import functools
import warnings
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import safetensors_mlir
import torch
import torch.utils._pytree
import torch_mlir
from mlir.ir import (
    BF16Type,
    ComplexType,
    Context,
    F16Type,
    F32Type,
    F64Type,
    Float8E4M3FNType,
    IntegerType,
    Operation,
    RankedTensorType,
    Value,
)
from safetensors.torch import _find_shared_tensors, save_file
from torch._decomp import remove_decompositions
from torch.export._trace import _export
from torch_mlir.dialects import torch as torch_d
from torch_mlir.extras.fx_decomp_util import get_decomposition_table
from torch_mlir.extras.fx_importer import FxImporter, FxImporterHooks, InputInfo
from torch_mlir.fx import export_and_import
from transformers import DynamicCache

from gml.asset_manager import AssetManager
from gml.register_submodules import submodule_registration_workarounds
from gml.version_utils import is_transformers_version_greater_or_equal


def _default_decomposition_denylist():
    """These ops will not be decomposed by default."""
    return [
        torch.ops.aten.full.default,
        torch.ops.aten.upsample_bilinear2d.vec,
    ]


_registered_dynamic_cache_pytree_node = False


def register_dynamic_cache_pytree_node():
    """
    Registers flattening/unflattening for transformers.DynamicCache
    Pytree is a representation of tensor collections used inside torch.export.
    """

    global _registered_dynamic_cache_pytree_node
    if _registered_dynamic_cache_pytree_node:
        return
    _registered_dynamic_cache_pytree_node = True

    def flatten_cache_with_keys(dynamic_cache: DynamicCache):
        return [
            (
                torch.utils._pytree.MappingKey(i),
                list(value),
            )
            for i, value in enumerate(dynamic_cache.to_legacy_cache())
        ], None

    def flatten_cache(dynamic_cache: DynamicCache):
        flattened, ctx = flatten_cache_with_keys(dynamic_cache)
        return [v for _, v in flattened], ctx

    def unflatten_cache(flattened: Iterable[Any], context: Any):
        return DynamicCache.from_legacy_cache(flattened)

    register_fn = torch.utils._pytree.register_pytree_node
    if is_transformers_version_greater_or_equal("4.50.0"):
        # TODO(james): Remove this when we support passing in KV Cache in arbitrary order.
        # We currently only support passing in KV Cache in [k0, v0, k1, v1, ...] order,
        # so we need to override transformers pytree registration for DynamicCache.
        # Overriding the registration allows us to flatten the cache how we expect.
        # However, this will break other people's code that relies on the default
        # transformers behaviour so we should remove this eventually.
        def register_fn(*args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                torch.utils._pytree._private_register_pytree_node(*args, **kwargs)

    register_fn(
        DynamicCache,
        flatten_cache,
        unflatten_cache,
        serialized_type_name=f"{DynamicCache.__module__}.{DynamicCache.__name__}",
        flatten_with_keys_fn=flatten_cache_with_keys,
    )


@contextlib.contextmanager
def _patch_aot_export_module():
    """This contextmanager prevents PyTorch dispatch from running when calling aot_export_module.

    This patch is necessary because not all callers of `aot_export_module` expose the pre_dispatch flag.
    For example, `ExportedProgram.run_decompositions` which is called by `torch_mlir.fx.export_and_import` doesn't
    expose the pre_dispatch flag.

    Without setting `pre_dispatch=True`, PyTorch dispatch will run before tracing which causes certain operations to be decomposed.
    For example, `upsample_nearest2d` will be decomposed into aten.index.Tensor calls. This is undesirable for runtimes that provide
    optimized implementations of the equivalent of `upsample_nearest2d`.
    """
    import torch._functorch.aot_autograd

    orig = torch._functorch.aot_autograd.aot_export_module
    torch._functorch.aot_autograd.aot_export_module = functools.partial(
        orig, pre_dispatch=True
    )
    yield
    torch._functorch.aot_autograd.aot_export_module = orig


_torch_dtype_to_builtin_element_type = {
    torch.float16: lambda: F16Type.get(),
    torch.bfloat16: lambda: BF16Type.get(),
    torch.float32: lambda: F32Type.get(),
    torch.float64: lambda: F64Type.get(),
    torch.uint8: lambda: IntegerType.get_unsigned(8),
    torch.int8: lambda: IntegerType.get_signless(8),
    torch.int16: lambda: IntegerType.get_signless(16),
    torch.int32: lambda: IntegerType.get_signless(32),
    torch.int64: lambda: IntegerType.get_signless(64),
    torch.bool: lambda: IntegerType.get_signless(1),
    torch.qint8: lambda: IntegerType.get_signless(8),
    torch.quint8: lambda: IntegerType.get_unsigned(8),
    torch.complex32: lambda: ComplexType.get(F16Type.get()),
    torch.complex64: lambda: ComplexType.get(F32Type.get()),
    torch.complex128: lambda: ComplexType.get(F64Type.get()),
    # Quantized types.
    torch.float8_e4m3fn: lambda: Float8E4M3FNType.get(),
}


class TensorSet:
    def __init__(self):
        self._tensors: Dict[str, torch.Tensor] = dict()

    def add(self, tensor: torch.Tensor) -> str:
        shape_desc = "_".join([str(d) for d in tensor.shape])
        base_name = f"torch_tensor_{shape_desc}_{str(tensor.dtype)}"

        index = 0
        name = "{}_{}".format(base_name, index)
        while name in self._tensors and not torch.equal(tensor, self._tensors[name]):
            index += 1
            name = "{}_{}".format(base_name, index)

        self._tensors[name] = tensor
        return name

    def tensors(self) -> Dict[str, torch.Tensor]:
        return self._tensors


class SafetensorImporterHooks(FxImporterHooks):
    def __init__(
        self, asset_manager: AssetManager, state_dict: Dict[str, torch.Tensor]
    ):
        self._asset_mgr = asset_manager
        # TODO(james): shard weights into multiple shards.
        self.asset_name = "weights.shard0"
        self._tensors: Dict[str, torch.Tensor] = {}
        # Tensors that don't have a target name will be tracked and deduped in this set.
        self._fallback_tensors = TensorSet()

        # Any keys that are shared with multiple other keys will be remapped to the first key.
        # If you don't do this, safetensors throws an error that values are duplicated.
        # See: https://huggingface.co/docs/safetensors/torch_shared_tensors
        self._shared_remap: Dict[str, str] = {}
        for names in _find_shared_tensors(state_dict):
            if len(names) <= 1:
                continue
            # Sort the names to ensure deterministic behavior.
            sorted_names = sorted(names)
            for name in sorted_names[1:]:
                # All other tensors will be remapped to the first tensor name.
                self._shared_remap[name] = sorted_names[0]

    def resolve_literal(
        self,
        gni: "torch_mlir.extras.fx_importer.GraphNodeImporter",
        literal: Any,
        info: Optional[InputInfo],
    ) -> Optional[Value]:
        if not isinstance(literal, torch.Tensor):
            if (
                info is not None
                and info.input_spec is not None
                and info.input_spec.target is not None
            ):
                warnings.warn(
                    f"found non-tensor with target {info.input_spec.target}: {literal}",
                    stacklevel=2,
                )
            return None
        tensor = literal

        if info is None or info.input_spec.target is None:
            # Some models (like owlvit) have constant tensors without proper info metadata.
            # Generate a fallback name instead of skipping to avoid losing model data.
            tensor_name = self._fallback_tensors.add(tensor)
            warnings.warn(
                f"found tensor with no target name {tensor}, saving as {tensor_name}",
                stacklevel=2,
            )
        else:
            tensor_name = info.input_spec.target
            # Check to make sure we use the main tensor for any reused tensors.
            if tensor_name in self._shared_remap:
                tensor_name = self._shared_remap[tensor_name]

        ctx = gni._c

        self._tensors[tensor_name] = tensor

        file_attr = safetensors_mlir.FileAttr.get(ctx, self.asset_name)

        if tensor.dtype not in _torch_dtype_to_builtin_element_type:
            raise ValueError("unsupported torch dtype: {}".format(tensor.dtype))
        elem_type = _torch_dtype_to_builtin_element_type[tensor.dtype]()
        tensor_type = RankedTensorType.get(tuple(tensor.size()), elem_type)

        tensor_attr = safetensors_mlir.TensorAttr.get(
            tensor_type, file_attr, tensor_name
        )
        builtin_tensor = safetensors_mlir.tensor_ref(tensor_type, tensor_attr)

        vtensor_type = gni._cc.tensor_to_vtensor_type(tensor)
        return Operation.create(
            name="torch_c.from_builtin_tensor",
            results=[vtensor_type],
            operands=[builtin_tensor],
        ).result

    def save_tensors(self):
        file_path = self._asset_mgr.add_asset(self.asset_name)
        tensors = self._tensors
        for k in tensors:
            tensors[k] = tensors[k].contiguous()
        save_file(tensors, file_path)


def to_torch_mlir(
    model: torch.nn.Module,
    example_inputs: Sequence[torch.Tensor],
    dynamic_shapes: Optional[
        Sequence[Dict[int, Union[str, "torch.export.dynamic_shapes._Dim"]]]
    ] = None,
    decomposition_denylist: Optional[List[torch._ops.OperatorBase]] = None,
    weight_manager: Optional[AssetManager] = None,
    export_predispatch: bool = False,
):
    if dynamic_shapes is not None:
        for shape in dynamic_shapes:
            if not isinstance(shape, dict):
                continue
            for idx in shape:
                # Assign the value so that pyright understands the type.
                value = shape[idx]
                if isinstance(value, torch.export.dynamic_shapes._Dim):
                    continue
                shape[idx] = torch.export.Dim(value)
    if decomposition_denylist is None:
        decomposition_denylist = _default_decomposition_denylist()

    submodule_registration_workarounds(model)
    register_dynamic_cache_pytree_node()
    prog = _export(
        model,
        tuple(example_inputs),
        pre_dispatch=export_predispatch,
        strict=False,
        dynamic_shapes=dynamic_shapes,
    )
    decomp_table = get_decomposition_table()
    remove_decompositions(decomp_table, decomposition_denylist)
    hooks = None
    if weight_manager is not None:
        hooks = SafetensorImporterHooks(weight_manager, model.state_dict())

    context = Context()
    torch_d.register_dialect(context)
    safetensors_mlir.register_dialect(context)
    fx_importer = FxImporter(context=context, hooks=hooks)

    with _patch_aot_export_module():
        module = export_and_import(
            prog,
            *example_inputs,
            decomposition_table=decomp_table,
            fx_importer=fx_importer,
            # Exposes `info` to resolve_literal in safetensor importer hooks
            # allowing us to preserve the original tensor names.
            experimental_support_mutation=True,
        )

    if hooks is not None:
        hooks.save_tensors()

    try:
        module.operation.verify()
    except Exception as exc:
        raise Exception(
            "failed to verify converted torch model MLIR module: {}".format(module)
        ) from exc

    return module
