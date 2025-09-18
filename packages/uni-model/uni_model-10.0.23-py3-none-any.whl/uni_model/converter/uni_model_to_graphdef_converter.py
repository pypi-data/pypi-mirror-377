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

import os
from typing import List

from uni_model.model.behavioral.UniLayerConst import UniLayerConst
from uni_model.converter.const_compressor_holder import const_compressor_holder
from uni_model.converter.const_saving_method import ConstSavingMethod
from uni_model.converter.uni_model_path import UniModelPath
from uni_model.org.tensorflow.framework.graph_pb2 import GraphDef
from uni_model.org.tensorflow.framework.node_def_pb2 import NodeDef
from uni_model.converter.const_list import MODEL_DEF, MODEL_DEF_OP, NET_DEF, NET_DEF_OP, NAME_ATTR, \
    ID_ATTR, INPUT_SPLITTER, ORDINAL, METADATA, VERSION
from uni_model.converter.nodedef_generator import NodeDefGenerator
from uni_model.model.additional.const_extra_attr import ConstExtraAttr
from uni_model.model.uni_graph import UniGraph
from uni_model.model.uni_model import UniModel
from uni_model.version import __version__

out_const_saving_method_str = "outConstSavingMethod"
class UniModelToGraphDefConverter:
    @staticmethod
    def convert(model: UniModel, uni_model_path: UniModelPath,
                const_saving_method: ConstSavingMethod = ConstSavingMethod.OUT_MODEL_FILE,
                skip_compaction: bool = True):
        if uni_model_path.txt_format and const_saving_method==ConstSavingMethod.OUT_MODEL_FILE:
            print("Using text format (pbtxt extension) and IN_MODEL_FILE const saving method is incompatible. "
                  "Changing to OUT_MODEL_FILE")
        fixed_const_saving_method = ConstSavingMethod.IN_MODEL_FILE if uni_model_path.txt_format else const_saving_method
        if fixed_const_saving_method == ConstSavingMethod.OUT_MODEL_FILE:
            model.add_metadata_entry(out_const_saving_method_str, "true")
        model.add_metadata_entry(VERSION,  __version__)
        UniModelToGraphDefConverter._serialize(
            UniModelToGraphDefConverter._cast_model(model, fixed_const_saving_method, skip_compaction), uni_model_path, fixed_const_saving_method
        )

    @staticmethod
    def _cast_model(model: UniModel, const_saving_method: ConstSavingMethod, skip_compaction: bool) -> GraphDef:
        model_properties_node = UniModelToGraphDefConverter._generate_model_properties_node(model)
        graph_properties_nodes = [UniModelToGraphDefConverter._generate_graph_properties_node(g)
                                  for g in model.uni_graphs]
        graph_nodes = [UniModelToGraphDefConverter._generate_graph_nodes(g, const_saving_method, skip_compaction) for g in model.uni_graphs]
        graphdef = GraphDef()
        graphdef.node.extend([model_properties_node] + graph_properties_nodes +
                             [i for spec_graph_nodes in graph_nodes for i in spec_graph_nodes])
        return graphdef

    @staticmethod
    def _serialize(model: GraphDef, uni_model_path: UniModelPath, const_saving_method: ConstSavingMethod):
        if not os.path.exists(uni_model_path.directory):
            raise ValueError(f"invalid directory was given: {uni_model_path.directory}")
        write_instructions = "w" if uni_model_path.txt_format else "wb"
        model_serialized = str(model) if uni_model_path.txt_format else model.SerializeToString(deterministic=True)
        f = open(uni_model_path.to_absolute_file_name(), write_instructions)
        f.write(model_serialized)
        f.close()
        if const_saving_method == ConstSavingMethod.OUT_MODEL_FILE:
            const_file = uni_model_path.to_const_file()
            const_compressor_holder.save_to_file(const_file)
            const_compressor_holder.clean_data()


    @staticmethod
    def _generate_model_properties_node(model: UniModel) -> NodeDef:
        node = NodeDef()
        node.name = MODEL_DEF
        node.op = MODEL_DEF_OP
        metadata_casted = {f"{METADATA}-{key}": NodeDefGenerator.get_content_in_correct_type(model.metadata[key]) for key in model.metadata}
        for key, value in metadata_casted.items():
            node.attr[key].CopyFrom(value)
        return node

    @staticmethod
    def _generate_graph_properties_node(graph: UniGraph) -> NodeDef:
        node = NodeDef()
        node.name = NET_DEF + "_" + graph.id
        node.op = NET_DEF_OP
        node.attr[NAME_ATTR] \
            .CopyFrom(NodeDefGenerator.get_content_in_correct_type(graph.name))
        node.attr[ID_ATTR].CopyFrom(NodeDefGenerator.get_content_in_correct_type(graph.id))
        node.attr[ORDINAL].CopyFrom(NodeDefGenerator.get_content_in_correct_type(graph.ordinal))
        metadata_casted = {f"{METADATA}-{key}": NodeDefGenerator.get_content_in_correct_type(graph.metadata[key]) for
                           key in graph.metadata}
        for key, value in metadata_casted.items():
            node.attr[key].CopyFrom(value)
        return node

    @staticmethod
    def _generate_graph_nodes(graph: UniGraph, const_saving_method: ConstSavingMethod, skip_compaction: bool) -> List[NodeDef]:
        layer_input = {}
        for e in graph.edges:
            if e.to_node.name not in layer_input:
                layer_input[e.to_node.name] = []
            layer_input[e.to_node.name].append(e.from_node.name + INPUT_SPLITTER + str(e.from_index) + INPUT_SPLITTER
                                               + str(e.to_index))
        compact_nodes = graph.layer_nodes if skip_compaction else [n.compact() for n in graph.layer_nodes]
        if const_saving_method == ConstSavingMethod.OUT_MODEL_FILE:
            for node in compact_nodes:
                if isinstance(node, UniLayerConst):
                    node._set_extra(ConstExtraAttr(const_compressor_holder.hold_const_float_data(node.float_data.flatten().tolist()),
                                                   const_compressor_holder.hold_const_fixed_point_repr(node.fixed_point_repr.flatten().tolist(), node.dtype.value_n_bits)))
        return [n.to_node_def(layer_input.get(n.name, []), graph.id) for n in compact_nodes]
