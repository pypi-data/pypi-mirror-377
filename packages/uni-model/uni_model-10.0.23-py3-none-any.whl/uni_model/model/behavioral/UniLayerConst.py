# -------------------------------------------------------------------------------
# (c) Copyright 2023 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
from dataclasses import dataclass, field
import numpy as np

from uni_model.auto_generated.UniLayerConstStructure import UniLayerConstStructure
from uni_model.validation.validation_cfg import ValidationCfg
from uni_model.validation.error_builder import ErrorBuilder
from uni_model.validation.error_codes import ErrorCodes
from uni_model.validation.uni_model_exception import UniModelException
from uni_model.utils.immute import immute
from uni_model.converter.nodedef_generator import NodeDefGenerator
from uni_model.org.tensorflow.framework.attr_value_pb2 import AttrValue
from uni_model.model.accuracy.const import _Const
from uni_model.model.accuracy.quantized_const import _QuantizedConst


@dataclass(frozen=True,  eq=False)
class UniLayerConst(UniLayerConstStructure):
    _hash_calculated: int = field(default=None, init=False, repr=False)
    _const_impl: _Const = field(default=None, init=False, repr=False)
    _const_compacted_impl: _Const = field(default=None, init=False, repr=False)
    _compact_impl: _QuantizedConst = field(default=None, init=False, repr=False)

    def __eq__(self, other):
        self_data = self.const_compacted_impl.fixed_point_repr if isinstance(self.const_compacted_impl, _QuantizedConst) \
                                                         and self.const_compacted_impl.fixed_point_repr.size > 0 else self.float_data
        other_data = other.const_compacted_impl.fixed_point_repr if isinstance(other.const_compacted_impl, _QuantizedConst) \
                                                                    and other.const_compacted_impl.fixed_point_repr.size > 0 else other.float_data

        if self.name != other.name or not np.allclose(self_data, other_data) or self.dtype != other.dtype or\
                self.out_shapes != other.out_shapes or self.history != other.history or any(
            [v != other.extended_attr[k] if not isinstance(v, float) else not np.allclose(v, other.extended_attr[k])
             for k, v in self.extended_attr.items()]):
            return False
        return True

    def validate(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, graph_id: str):
        super().validate(validation_cfg, error_builder, graph_id)
        if len(self.fixed_point_repr) > 0:
            legal_range = range(0, 2 ** self.dtype.value_n_bits)
            not_in_range = [index for index in self.fixed_point_repr.flatten().tolist() if index not in legal_range]
            if len(not_in_range) > 0:
                raise UniModelException(ErrorCodes.CIDMBIN,
                                        f"Node const {self.name} forbidden indices: {not_in_range}. Used {self.dtype.value_n_bits} valueNBits. {ErrorCodes.CIDMBIN.value}")
        self.dtype.validate(validation_cfg, error_builder, graph_id, self)
        if validation_cfg.validation_for_violation.require_accuracy_in_const_fixed_point_repr:
            if isinstance(self.const_compacted_impl, _QuantizedConst):
                self.dtype.validate_fixed_point_repr(self.name, self.float_data, self.const_compacted_impl.fixed_point_repr)

    def __post_init__(self):
        if len(self.out_dtypes) != 1:
            raise UniModelException(message="out_dtypes list must be with size 1")
        super().__post_init__()

    def __hash__(self):
        if self._hash_calculated is None:
            object.__setattr__(self, '_hash_calculated', self.calc_hash())
        return self._hash_calculated

    def calc_hash(self):
        data = self.const_compacted_impl.fixed_point_repr if isinstance(self.const_compacted_impl, _QuantizedConst) and \
                                                    self.const_compacted_impl.fixed_point_repr.size > 0 else self.float_data.astype(np.float32)

        return hash((self.name, tuple(data.flatten()),
                     tuple(self.fixed_point_repr), self.dtype, tuple(self.out_shapes), tuple(self.history),
                     immute(self.extended_attr)))

    @property
    def const_impl(self):
        if self._const_impl is None:
            object.__setattr__(self, '_const_impl', _Const(self.float_data, self.dtype))
        return self._const_impl

    @property
    def const_compacted_impl(self):
        if self._const_compacted_impl is None:
            # print(f"Compacting {self.name}")
            object.__setattr__(self, '_const_compacted_impl', self.const_impl.compact())
        return self._const_compacted_impl

    @property
    def compact_impl(self):
        if self._compact_impl is None:
            object.__setattr__(self, '_compact_impl',
                               _QuantizedConst(self.fixed_point_repr, self.dtype))
        return self._compact_impl

    @property
    def dtype(self):
        return self.out_dtypes[0]

    def _match_correct_type_to_attr(self, key: str, attr) -> AttrValue:
        if key == "fixed_point_repr":
            if self._get_extra() is None:
                return NodeDefGenerator.get_content_as_compressed_bytearray(attr.flatten().tolist(), self.dtype.value_n_bits)
            else:
                const_range = self._get_extra().to_attr()["indices_range"]
                return NodeDefGenerator.get_content_in_correct_type(const_range)
        elif key == "float_data":
            if self._get_extra() is None:
                return NodeDefGenerator.get_content_in_correct_type(attr.flatten().tolist())
            else:
                const_range = self._get_extra().to_attr()["float_range"]
                return NodeDefGenerator.get_content_in_correct_type(const_range)
        elif key == "out_dtypes":
            return NodeDefGenerator.get_content_in_correct_type(attr[0])
        else:
            return NodeDefGenerator.get_content_in_correct_type(attr)

    def _after_matching(self):
        self._set_extra(None)

    def _rename_key(self, key) -> str:
        if key in ["outDtypes", "out_dtypes"]:
            return "dtype"
        else:
            return key

    def compact(self):
        if len(self.fixed_point_repr) > 0:
            return self
        else:
            if isinstance(self.const_compacted_impl, _QuantizedConst):
                from uni_model.utils.uni_layer_const_helper import _create_const_with_fixed_point_repr_data
                compacted = _create_const_with_fixed_point_repr_data(self.name,
                                                           self.const_compacted_impl.fixed_point_repr,
                                                           self.const_compacted_impl.qtype, [self.out_shapes[0]],
                                                           self.history)
                compacted._set_extra(self._get_extra())
                return compacted
            else:
                return self

    def decompact(self):
        if len(self.fixed_point_repr) > 0:
            from uni_model.utils.uni_layer_const_helper import create_const_with_data
            return create_const_with_data(self.name, self.compact_impl.values, self.dtype,
                                                self.history)
        else:
            return self

    def _ignore_key(self, key, value):
        return key.startswith('_')

    def get_fixed_point_repr_tensor(self):
        if len(self.fixed_point_repr) == 0:
            if isinstance(self.const_compacted_impl, _QuantizedConst):
                return self.const_compacted_impl.fixed_point_repr
            else:
                return None
        else:
            return self.fixed_point_repr

    def get_float_tensor(self):
        if len(self.float_data) > 0:
            return self.float_data
        else:
            return self.compact_impl.values