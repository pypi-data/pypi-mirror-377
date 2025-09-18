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

from typing import Dict, List
import stringcase

from uni_model.model.quantization.Dtype import Dtype
from uni_model.model.quantization.QtypePerTensor import QtypePerTensor
from uni_model.model.quantization.Dfloat import Dfloat
from uni_model.model.quantization.QtypePerAxis import QtypePerAxis
from uni_model.model.quantization.QtypePerElement import QtypePerElement
from uni_model.auto_generated import PlaceholderDtype, TensorDesc
from uni_model.model.quantization.LutPerAxis import LutPerAxis
from uni_model.model.quantization.LutPerTensor import LutPerTensor
from uni_model.auto_generated.Layout import Layout
from uni_model.auto_generated.Semantic import Semantic
from uni_model.auto_generated.ShapeImpl import ShapeImpl
from uni_model.auto_generated import EmptyShape
from uni_model.converter.const_compressor_holder import const_compressor_holder, ConstCompressorHolder
from uni_model.org.tensorflow.framework.attr_value_pb2 import AttrValue
from uni_model.org.tensorflow.framework.node_def_pb2 import NodeDef
from uni_model.auto_generated.ResizeMethod import ResizeMethod
from uni_model.auto_generated.DataFormat import DataFormat
from uni_model.auto_generated.SerializationInfo import SerializationInfo
from uni_model.auto_generated.UniSliceConfig import UniSliceConfig
from uni_model.converter.const_list import HASHED
from uni_model.model.accuracy.min_max import MinMaxOpenEnded
from uni_model.utils.pair import Pair
import struct


class AttrValueGenerator:
    @classmethod
    def extract_attr(cls, node: NodeDef) -> Dict[str, object]:
        return_val = {}
        for k, v in node.attr.items():
            if node.op == "Const":
                if const_compressor_holder.has_const_to_read():
                    if k == "fixedPointRepr":
                        tv = const_compressor_holder.read_const_fixed_point_repr(cls._to_key_type_value(v), node.attr["dtype"].func.attr["valueNBits"].i)
                    elif k == "floatData":
                        tv = const_compressor_holder.read_const_float_data(cls._to_key_type_value(v))
                    else:
                        tv = cls._to_key_type_value(v)
                else:
                    if k == "fixedPointRepr":
                        value_n_bits = node.attr["dtype"].func.attr["valueNBits"].i
                        data = v.func.attr["data"].s
                        bytes_length = ConstCompressorHolder.nbits_to_bytes(value_n_bits)
                        struct_size_definition = ConstCompressorHolder.nbits_to_struct_size_definition(value_n_bits)
                        tv = list(struct.unpack(struct_size_definition * (len(data) // bytes_length), data))
                    else:
                        tv = cls._to_key_type_value(v)

            else:
                tv = cls._to_key_type_value(v)
            if tv is not None:
                return_val[k] = tv
        return return_val

    @classmethod
    def _to_key_type_value(cls, obj: AttrValue):
        if obj.HasField("s"):
            return getattr(obj, "s").decode()
        elif obj.HasField("b"):
            return getattr(obj, "b")
        elif obj.HasField("func"):
            return getattr(cls, f"_generate_{stringcase.snakecase(obj.func.name)}")(obj)
        elif obj.HasField("f"):
            return getattr(obj, "f")
        elif obj.HasField("i"):
            return getattr(obj, "i")
        elif obj.HasField("list"):
            return cls._to_key_type_value_list(obj)
        else:
            return None

    @classmethod
    def _to_key_type_value_list(cls, obj: AttrValue) -> List[object]:
        return_value = []
        for field in obj.list.ListFields():
            if field[0].name == "s":
                return_value.extend([s.decode() for s in obj.list.s])
            elif field[0].name == "list":
                # todo
                raise NotImplementedError
            elif field[0].name == "func":
                return_value.extend(
                    [getattr(cls, f"_generate_{stringcase.snakecase(e.name)}")(e) for e in obj.list.func])
            else:
                return_value.extend([e for e in getattr(obj.list, field[0].name)])
        return return_value

    @classmethod
    def _generate_pair(cls, obj: AttrValue) -> Pair:
        if hasattr(obj, "func"):
            return Pair(first=cls._to_key_type_value(obj.func.attr['first']), second=cls._to_key_type_value(obj.func.attr['second']))
        else:
            return Pair(first=cls._to_key_type_value(obj.attr['first']), second=cls._to_key_type_value(obj.attr['second']))

    @classmethod
    def _generate_bytearray(cls, obj: AttrValue) -> List:
        raw_data = obj.func.attr['data'].s
        return [raw_data[i:i + 1] for i in range(0, len(raw_data))]

    @classmethod
    def _generate_hash(cls, obj: AttrValue) -> Dict:
        return {k[len(HASHED) + 1:]: cls._to_key_type_value(v) for k, v in obj.func.attr.items()}

    @classmethod
    def _generate_list(cls, obj: AttrValue) -> List:
        return cls._to_key_type_value(obj.attr[""])

    @classmethod
    def _generate_hashed(cls, obj: AttrValue) -> Dict:
        return {k[len(HASHED):]: cls._to_key_type_value(v) for k, v in obj.attr}

    @classmethod
    def _generate_serialization_info(cls, obj: AttrValue) -> SerializationInfo:
        if hasattr(obj, 'func'):
            return SerializationInfo(axis=cls._to_key_type_value(obj.func.attr['axis']),
                                     simd_axis=cls._to_key_type_value(obj.func.attr['simdAxis']))
        else:
            return SerializationInfo(axis=cls._to_key_type_value(obj.attr['axis']),
                                     simd_axis=cls._to_key_type_value(obj.attr['simdAxis']))

    @classmethod
    def _generate_dtype(cls, obj: AttrValue) -> Dtype:
        if hasattr(obj, "func"):
            return Dtype(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']))
        else:
            return Dtype(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']))

    @classmethod
    def _generate_dfloat(cls, obj: AttrValue) -> Dfloat:
        if hasattr(obj, "func"):
            return Dfloat(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']))
        else:
            return Dfloat(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']))

    @classmethod
    def _generate_qtype_per_axis(cls, obj: AttrValue) -> QtypePerAxis:
        if hasattr(obj, "func"):
            return QtypePerAxis(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']),
                                axis=cls._to_key_type_value(obj.func.attr['axis']),
                                min_maxes=cls._to_key_type_value(obj.func.attr['minMaxes']))
        else:
            return QtypePerAxis(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']),
                                axis=cls._to_key_type_value(obj.attr['axis']),
                                min_maxes=cls._to_key_type_value(obj.attr['minMaxes']))


    @classmethod
    def _generate_qtype_per_element(cls, obj: AttrValue) -> QtypePerElement:
        if hasattr(obj, "func"):
            return QtypePerElement(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']),
                                   min_maxes=cls._to_key_type_value(obj.func.attr['minMaxes']))
        else:
            return QtypePerElement(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']),
                                   min_maxes=cls._to_key_type_value(obj.attr['minMaxes']))

    @classmethod
    def _generate_lut_per_axis(cls, obj: AttrValue) -> LutPerAxis:
        if hasattr(obj, "func"):
            return LutPerAxis(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']),
                              table=cls._to_key_type_value(obj.func.attr['table']),
                              table_n_bits=cls._to_key_type_value(obj.func.attr['tableNBits']),
                              axis=cls._to_key_type_value(obj.func.attr['axis']),
                              min_maxes=cls._to_key_type_value(obj.func.attr['minMaxes']),
                              normalized_min=cls._to_key_type_value(obj.func.attr['normalizedMin']),
                              normalized_max=cls._to_key_type_value(obj.func.attr['normalizedMax']))
        else:
            return LutPerAxis(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']),
                              table=cls._to_key_type_value(obj.attr['table']),
                              table_n_bits=cls._to_key_type_value(obj.attr['tableNBits']),
                              axis=cls._to_key_type_value(obj.attr['axis']),
                              min_maxes=cls._to_key_type_value(obj.attr['minMaxes']),
                              normalized_min=cls._to_key_type_value(obj.attr['normalizedMin']),
                              normalized_max=cls._to_key_type_value(obj.attr['normalizedMax']))

    @classmethod
    def _generate_lut_per_tensor(cls, obj: AttrValue) -> LutPerTensor:
        if hasattr(obj, "func"):
            return LutPerTensor(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']),
                                table=cls._to_key_type_value(obj.func.attr['table']),
                                table_n_bits=cls._to_key_type_value(obj.func.attr['tableNBits']),
                                min_max=cls._to_key_type_value(obj.func.attr['minMax']),
                                normalized_min=cls._to_key_type_value(obj.func.attr['normalizedMin']),
                                normalized_max=cls._to_key_type_value(obj.func.attr['normalizedMax'])
                                )
        else:
            return LutPerTensor(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']),
                                table=cls._to_key_type_value(obj.attr['table']),
                                table_n_bits=cls._to_key_type_value(obj.attr['tableNBits']),
                                min_max=cls._to_key_type_value(obj.attr['minMax']),
                                normalized_min=cls._to_key_type_value(obj.attr['normalizedMin']),
                                normalized_max=cls._to_key_type_value(obj.attr['normalizedMax'])
                                )


    @classmethod
    def _generate_qtype_per_tensor(cls, obj: AttrValue) -> QtypePerTensor:
        if hasattr(obj, "func"):
            return QtypePerTensor(value_n_bits=cls._to_key_type_value(obj.func.attr['valueNBits']),
                                  min_max=cls._to_key_type_value(obj.func.attr['minMax']))
        else:
            return QtypePerTensor(value_n_bits=cls._to_key_type_value(obj.attr['valueNBits']),
                                  min_max=cls._to_key_type_value(obj.attr['minMax']))


    @classmethod
    def _generate_min_max_open_ended(cls, obj: AttrValue) -> MinMaxOpenEnded:
        if hasattr(obj, "func"):
            return MinMaxOpenEnded(cls._to_key_type_value(obj.func.attr['min']),
                          cls._to_key_type_value(obj.func.attr['max']))
        else:
            return MinMaxOpenEnded(cls._to_key_type_value(obj.attr['min']), cls._to_key_type_value(obj.attr['max']))


    @classmethod
    def _generate_dnn_slice_config(cls, obj: AttrValue) -> UniSliceConfig:
        return UniSliceConfig(begin=cls._to_key_type_value(obj.func.attr['begin']),
                              size=cls._to_key_type_value(obj.func.attr['size']))

    @classmethod
    def _generate_tensor_desc(cls, obj: AttrValue) -> TensorDesc:
        return TensorDesc(shape=cls._to_key_type_value(obj.func.attr['shape']),
                          qtype=cls._to_key_type_value(obj.func.attr['qtype']))

    @classmethod
    def _generate_resize_method(cls, obj: AttrValue) -> ResizeMethod:
        return ResizeMethod(cls._to_key_type_value(obj.func.attr['ordinal']))


    @classmethod
    def _generate_data_format(cls, obj: AttrValue) -> DataFormat:
         return DataFormat(cls._to_key_type_value(obj.func.attr['ordinal']))


    @classmethod
    def _generate_placeholder_dtype(cls, obj: AttrValue) -> PlaceholderDtype:
        return PlaceholderDtype(cls._to_key_type_value(obj.func.attr['ordinal']))

    @classmethod
    def _generate_layout(cls, obj: AttrValue) -> Layout:
        if hasattr(obj, "func"):
            return Layout(cls._to_key_type_value(obj.func.attr['semantics']))
        else:
            return Layout(cls._to_key_type_value(obj.attr['semantics']))

    @classmethod
    def _generate_semantic(cls, obj: AttrValue) -> Semantic:
        return Semantic(cls._to_key_type_value(obj.attr['ordinal']))

    @classmethod
    def _generate_shape_impl(cls, obj: AttrValue) -> ShapeImpl:
        if hasattr(obj, "func"):
            return ShapeImpl(cls._to_key_type_value(obj.func.attr['elements']))
        else:
            return ShapeImpl(cls._to_key_type_value(obj.attr['elements']))

    @classmethod
    def _generate_empty_shape(cls, obj: AttrValue) -> EmptyShape:
        return EmptyShape()

    @classmethod
    def _generate_int_range(cls, obj: AttrValue) -> range:
        return range(cls._to_key_type_value(obj.func.attr['from']), cls._to_key_type_value(obj.func.attr['to']))
