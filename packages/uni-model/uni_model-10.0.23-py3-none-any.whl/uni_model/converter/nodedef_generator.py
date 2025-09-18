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
import math
from enum import Enum
from typing import List, Dict

import numpy as np
import stringcase

from uni_model.org.tensorflow.framework.attr_value_pb2 import AttrValue, NameAttrList
from uni_model.converter.const_list import HASHED, LIST, BYTEARRAY


class NodeDefGenerator:
    @staticmethod
    def get_content_in_correct_type(content) -> AttrValue:
        # no long and double in python
        if content is None:
            return_val = None
        elif isinstance(content, bool):
            return_val = AttrValue()
            return_val.b = content
        elif isinstance(content, int):
            return_val = AttrValue()
            return_val.i = content
        elif isinstance(content, float):
            return_val = AttrValue()
            return_val.f = content
        elif isinstance(content, str):
            return_val = AttrValue()
            return_val.s = content.encode()
        elif isinstance(content, list) or isinstance(content, np.ndarray):
            return_val = NodeDefGenerator.get_content_in_correct_type_list(content)
        elif isinstance(content, dict):
            return_val = NodeDefGenerator.get_content_in_correct_type_map(content)
        else:
            return_val = NodeDefGenerator.get_content_in_correct_type_special(content)
        return return_val

    @staticmethod
    def get_content_in_correct_type_special(content) -> AttrValue:
        func = NodeDefGenerator._get_attr_as_dict(content)
        return_val = AttrValue()
        if content.__class__.__name__ == "range":
            func_name = "IntRange"
        else:
            func_name = content.__class__.__name__
        return_val.func.name = func_name
        for key in func:
            return_val.func.attr[stringcase.camelcase(key)].CopyFrom(func[key])
        return return_val

    @staticmethod
    def _get_attr_as_dict(content) -> Dict[str, AttrValue]:
        if isinstance(content, Enum):
            func = {"name": NodeDefGenerator.get_content_in_correct_type(content.name),
                    "ordinal": NodeDefGenerator.get_content_in_correct_type(content.value)}
        elif isinstance(content, range):
            func = {"from": NodeDefGenerator.get_content_in_correct_type(content.start),
                    "to": NodeDefGenerator.get_content_in_correct_type(content.stop)}
        elif hasattr(content, "__dict__"):
            func = {k: NodeDefGenerator.get_content_in_correct_type(v) for k, v in content.__dict__.items() if not k.startswith("_")}
        else:
            func = {k: NodeDefGenerator.get_content_in_correct_type(v) for k, v in content.items()}
        return func

    @staticmethod
    def get_content_in_correct_type_list(content: List, refer_as_bytearray: bool = False) -> AttrValue:
        def refer_as_bytearray_impl(content: List) -> AttrValue:
            return_val = AttrValue()
            uni_model_map = NameAttrList()
            uni_model_map.name = BYTEARRAY
            string_builder = AttrValue()
            string_builder.s = b''.join(content)
            uni_model_map.attr["data"].CopyFrom(string_builder)
            return_val.func.CopyFrom(uni_model_map)
            return return_val

        if refer_as_bytearray:
            return refer_as_bytearray_impl(content)
        if len(content) == 0:
            return_val = AttrValue()
            return_val.list.CopyFrom(AttrValue.ListValue())
            return return_val
        elif all([isinstance(c, bytes) for c in content]):
            return refer_as_bytearray_impl(content)
        else:
            return_val = AttrValue()
            return_val.list.CopyFrom(AttrValue.ListValue())
            if isinstance(content[0], bool):
                return_val.list.b.extend(content)
            elif isinstance(content[0], int):
                return_val.list.i.extend(content)
            elif isinstance(content[0], float):
                return_val.list.f.extend(content)
            elif isinstance(content[0], str):
                return_val.list.s.extend([e.encode() for e in content])
            elif isinstance(content[0], list) or isinstance(content[0], np.ndarray):
                for e in content:
                    member = NameAttrList()
                    member.name = LIST
                    correct = NodeDefGenerator.get_content_in_correct_type_list(e)
                    member.attr[""].CopyFrom(correct)
                    return_val.list.func.append(member)
            else:
                for e in content:
                    member = NameAttrList()
                    member.name = e.__class__.__name__
                    for attr_name, attr_val in NodeDefGenerator._get_attr_as_dict(e).items():
                        member.attr[stringcase.camelcase(attr_name)].CopyFrom(attr_val)
                    return_val.list.func.append(member)
            return return_val

    @staticmethod
    def get_content_in_correct_type_map(content: Dict) -> AttrValue:
        attr = {f"{HASHED}_{k}": NodeDefGenerator.get_content_in_correct_type(v) for k, v in content.items()}
        uni_model_map = NameAttrList()
        uni_model_map.name = HASHED
        for k, v in attr.items():
            uni_model_map.attr[k].CopyFrom(v)
        return_val = AttrValue()
        return_val.func.CopyFrom(uni_model_map)
        return return_val

    @staticmethod
    def get_content_as_compressed_bytearray(content: List[int], n_bits: int):
        compressed = [i.to_bytes(math.ceil(n_bits / 8), byteorder="little") for i in content]
        return NodeDefGenerator.get_content_in_correct_type_list(compressed, refer_as_bytearray=True)
