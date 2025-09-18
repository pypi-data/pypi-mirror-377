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

import typing
from abc import ABC
from dataclasses import dataclass, field, fields
from typing import List, ClassVar, Dict, Any

from uni_model.auto_generated.Shape import Shape
from uni_model.model.quantization.Dtype import Dtype
from uni_model.org.tensorflow.framework.node_def_pb2 import NodeDef
from uni_model.converter.const_list import GRAPH_ID
from uni_model.converter.nodedef_generator import NodeDefGenerator
import stringcase
from uni_model.org.tensorflow.framework.attr_value_pb2 import AttrValue
from uni_model.utils.immute import immute
from uni_model.validation.error_builder import ErrorBuilder
from uni_model.validation.error_report import ErrorReport
from uni_model.validation.validation_cfg import ValidationCfg, ReportForValidationViolation
import copy
import abc
import numpy as np
from uni_model.validation.uni_model_exception import UniModelException
from uni_model.utils.locate_class import locate_class

extra = "extra"


class LayerExtraNotSerialized(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "to_attr") and callable(subclass.to_attr)

    def to_attr(self):
        raise NotImplementedError


@dataclass(frozen=True)
class UniLayerBase(ABC):
    name: str


@dataclass(frozen=True)
class UniLayer(UniLayerBase):
    out_shapes: List[Shape] = field(default_factory=list)
    out_dtypes: List[Dtype] = field(default_factory=list)
    # history is used as debug fields
    history: List[str] = field(default_factory=list)
    extended_attr: Dict[str, Any] = field(default_factory=dict)
    op: ClassVar = "undefined"
    _valid_input_range: ClassVar = range(1, 2)
    _valid_output_range: ClassVar = range(1, 2)
    input_names: ClassVar = []
    output_names: ClassVar = []

    # this 2 following functions are less immutable, but this extra attr is only for developing and not for serializing
    def _set_extra(self, extra_attr: LayerExtraNotSerialized):
        object.__setattr__(self, extra, extra_attr)

    def _get_extra(self):
        if hasattr(self, extra):
            return object.__getattribute__(self, extra)
        else:
            return None

    @property
    def valid_input_range(self):
        return self._valid_input_range

    @property
    def valid_output_range(self):
        return self._valid_output_range

    def __hash__(self):
        return hash((tuple(self.out_shapes), tuple(self.out_dtypes), tuple(self.history),
                     immute(self.extended_attr)))

    def set_attr(self, key: str, value: Any):
        new_layer = copy.deepcopy(self)
        # assert self == new_layer
        new_layer.extended_attr[key] = value
        return new_layer

    def input_name_for_index(self, i: int) -> str:
        if i not in self.valid_input_range:
            raise UniModelException(message=f"Index {i} is out if bounds for range {self.valid_input_range}")
        if len(self.input_names) == 0:
            return f"input{i}"
        else:
            return self.input_names[i]

    def output_name_for_index(self, i: int) -> str:
        if i not in self.valid_output_range:
            raise UniModelException(message=f"Index {i} is out if bounds for range {self.valid_output_range}")
        if len(self.output_names) == 0:
            return f"output{i}"
        else:
            return self.output_names[i]

    def compact(self):
        return self

    def decompact(self):
        return self

    @property
    def ignored_keys(self):
        return ["name", "op"]

    def __post_init__(self):
        def check_inner_value(node_name, param_name_inner, param_value_inner, param_type_inner):
            if param_type_inner is not typing.Any and not isinstance(param_value_inner, param_type_inner):
                raise UniModelException(message=
                    f"In node {node_name}: type of {param_name_inner} must be {param_type_inner} and it's not. Cannot proceed")

        types = typing.get_type_hints(self.__class__)
        for param_name, param_type in types.items():
            if param_type is not typing.ClassVar and hasattr(self, param_name) and not param_name.startswith("_"):
                param_value = getattr(self, param_name)
                if param_value is not None:
                    if str(param_type).startswith("typing"):
                        param_type_str = str(param_type)[len("typing."):]
                        if param_type_str.startswith("List"):
                            if not isinstance(param_value, list):
                                if isinstance(param_value, np.ndarray) and param_value.dtype in \
                                        [np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16,
                                         np.uint32, np.uint64, np.float32, np.float64]:
                                    param_value = param_value.flatten().tolist()
                                    object.__setattr__(self, param_name, param_value)
                                else:
                                    raise UniModelException(message=f"Type of {param_name} must be list and it's not. Cannot proceed")
                            param_type_str_as_str = param_type_str[len("List["):-1].split(",")[0]
                            param_type_str_as_str_split = param_type_str_as_str.split(".")
                            # if len(param_type_str_as_str_split) > 3 and param_type_str_as_str_split[-1] == \
                            #         param_type_str_as_str_split[-2] and param_type_str_as_str_split[
                            #     -3] in ["auto_generated", "behavioral", "quantization"]:
                            #     param_type_str_as_str = ".".join(param_type_str_as_str_split)
                            inner_type_of_list = locate_class(param_type_str_as_str_split)
                            if inner_type_of_list is None:
                                if "List[int]" in param_type_str_as_str:
                                    inner_type_of_list = list
                            for v in param_value:
                                check_inner_value(self.name, f"{param_name} member", v, inner_type_of_list)
                        elif param_type_str.startswith("Dict"):
                            if not isinstance(param_value, dict):
                                raise UniModelException(message=f"Type of {param_name} must be dict and it's not. Cannot proceed")
                            inner_type_of_dict = [locate_class(t) for t in param_type_str[len("Dict["):-1].split(",")]
                            [check_inner_value(self.name, f"{param_name} key", k, inner_type_of_dict[0]) for k in
                             param_value.keys()]
                            if inner_type_of_dict[1] != typing.Any:
                                raise UniModelException(message="Not handled other that any type in dict")
                        else:
                            raise UniModelException(message="Not handled type validation")
                    else:
                        if isinstance(param_value, np.ndarray) and param_value.size == 1 and param_value.dtype in [
                            np.int32, np.int64] and param_type != np.ndarray:
                            object.__setattr__(self, param_name, int(param_value))
                        elif isinstance(param_value, np.ndarray) and param_value.size == 1 and param_value.dtype in [
                            np.float32, np.float64] and param_type != np.ndarray:
                            object.__setattr__(self, param_name, float(param_value))
                        else:
                            check_inner_value(self.name, param_name, param_value, param_type)

    def validate(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, graph_id: str):
        if validation_cfg.validation_for_violation.require_out_q_info_equals_output_size and len(self.out_dtypes) != 0:
            if len(self.out_dtypes) not in self.valid_output_range:
                error_builder.log_error(
                    ErrorReport(ReportForValidationViolation.OQIEOS, graph_id=graph_id, layer_name=self.name, op=self.op,
                                extra_information=f"OutQTypes size is {len(self.out_dtypes)} but range is {self.valid_output_range}"))
        for dtype in self.out_dtypes:
            dtype.validate(validation_cfg, error_builder, graph_id, self)

        if validation_cfg.validation_for_violation.require_match_qtype_and_shapes and len(self.out_shapes) > 0 and len(
                self.out_dtypes) > 0:
            match = [dtype.validate_shapes(shapes) for dtype, shapes in zip(self.out_dtypes, self.out_shapes)]
            if len(self.out_dtypes) != len(self.out_shapes) or any([m is not None for m in match]):
                error_builder.log_error(
                    ErrorReport(ReportForValidationViolation.QTMMS, graph_id=graph_id, layer_name=self.name, op=self.op,
                                extra_information="".join([m for m in match if m is not None])))

    def validate_shape_in_reshape(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, shape: Shape,
                                  graph_id: str):
        if validation_cfg.validation_for_violation.require_legal_shape_in_reshape:
            non_positive_members = [s for s in shape.elements if s <= 0]
            if non_positive_members.count(-1) > 1 or any([v != - 1 for v in non_positive_members]):
                error_builder.log_error(ErrorReport(ReportForValidationViolation.LSIRS, graph_id=graph_id, op=self.op,
                                                    layer_name=self.name, extra_information=f"but shape is {shape}"))

    def _match_correct_type_to_attr(self, key: str, attr) -> AttrValue:
        return NodeDefGenerator.get_content_in_correct_type(attr)

    def _after_matching(self):
        pass

    def _rename_key(self, key) -> str:
        return key

    def _ignore_key(self, key, value):
        if key == "extended_attr":
            return len(value) == 0
        else:
            return key in self.ignored_keys

    def to_node_def(self, inputs: List[str], graph_id: str) -> NodeDef:
        from uni_model.model.extended.extended_uni_model import ExtendedUniLayer
        node_to_convert = self.to_wildcard() if isinstance(self, ExtendedUniLayer) else self
        nodedef = NodeDef()
        nodedef.name = node_to_convert.name
        nodedef.op = node_to_convert.op
        nodedef.input.extend(inputs)
        fields_of_layer = {f.name: f for f in fields(node_to_convert)}
        for key, value in vars(node_to_convert).items():
            if not self._ignore_key(key, value):
                value_casted = node_to_convert._match_correct_type_to_attr(key, value)
                if value_casted is not None and key != extra and fields_of_layer[key].init:
                    nodedef.attr[self._rename_key(stringcase.camelcase(key))].CopyFrom(value_casted)
        self._after_matching()
        nodedef.attr[GRAPH_ID].CopyFrom(NodeDefGenerator.get_content_in_correct_type(graph_id))
        return nodedef


@dataclass(frozen=True)
class DeprecatedUniLayer(UniLayer):
    suggestion: ClassVar = "unspecified"

    def __post_init__(self):
        print(f"This layer is deprecated. Use layer {self.suggestion} instead.")
        super().__post_init__()
