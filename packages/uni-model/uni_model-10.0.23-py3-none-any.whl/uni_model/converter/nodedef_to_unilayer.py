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
'''
Created on 7/24/23

@author: zvikaa
'''
from dataclasses import fields
from importlib import import_module

import numpy as np

from uni_model.converter.attr_value_generator import AttrValueGenerator
from uni_model.converter.const_list import GRAPH_ID
from uni_model.model.extended.extended_unilayer_instructions_manager import extended_unilayer_instructions_manager
from uni_model.org.tensorflow.framework.node_def_pb2 import NodeDef
import stringcase
from uni_model.auto_generated.UniLayerWildcard import UniLayerWildcard


def node_to_uni_layer(node: NodeDef):
    attr = AttrValueGenerator.extract_attr(node)
    attr_for_ctor = {stringcase.snakecase(k): v for k, v in attr.items()
                     if k not in [GRAPH_ID]}
    attr_for_ctor.update({"name": node.name})
    if node.op == "Const":
        attr_for_ctor.update({"out_dtypes": [attr_for_ctor["dtype"]]})
        del attr_for_ctor["dtype"]
        shape = attr_for_ctor["out_shapes"][0].elements
        float_data = np.array(attr_for_ctor["float_data"]).reshape(shape) if len(attr_for_ctor["float_data"]) > 0 else np.array([])
        fixed_point_repr = np.array(attr_for_ctor["fixed_point_repr"]).reshape(shape) if len(
            attr_for_ctor["fixed_point_repr"]) > 0 else np.array([])
        attr_for_ctor.update({"float_data": float_data})
        attr_for_ctor.update({"fixed_point_repr": fixed_point_repr})
    try:
        module = import_module(f"uni_model.auto_generated.UniLayer{node.op}")
    except ModuleNotFoundError:
        module = import_module(f"uni_model.model.behavioral.UniLayer{node.op}")
    klass = getattr(module, f"UniLayer{node.op}")
    for f in fields(klass):
        if not f.init and f.name in attr_for_ctor:
            del attr_for_ctor[f.name]
    instance = klass(**attr_for_ctor)

    if isinstance(instance, UniLayerWildcard):
        return extended_unilayer_instructions_manager.wildcard_to_extended_layer(instance)
    else:
        return instance
