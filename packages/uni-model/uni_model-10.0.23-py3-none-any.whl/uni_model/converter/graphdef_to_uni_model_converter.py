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
import os.path
import re
from typing import List, Dict, Callable

from uni_model import UniLayerWildcard
from uni_model.converter.const_compressor_holder import const_compressor_holder
from uni_model.converter.nodedef_to_unilayer import node_to_uni_layer
from uni_model.converter.uni_model_to_graphdef_converter import out_const_saving_method_str
from uni_model.org.tensorflow.framework.graph_pb2 import GraphDef
from uni_model.converter.attr_value_generator import AttrValueGenerator
from uni_model.converter.const_list import MODEL_DEF_OP, NET_DEF_OP, GRAPH_ID, ID_ATTR, INPUT_SPLITTER, NAME_ATTR, \
    ORDINAL, UNIMODEL, UNIMODEL_CONST_EXT, METADATA
from uni_model.model.extended.extended_unilayer_instructions_manager import extended_unilayer_instructions_manager
from uni_model.model.generator.uni_model_generator import UniModelGenerator
from uni_model.model.uni_layer import UniLayer
from uni_model.model.uni_model import UniModel, UniModelBuilder
from uni_model.validation.error_codes import ErrorCodes
from uni_model.validation.uni_model_exception import UniModelException


class GraphDefToUniModelConverter:

    @staticmethod
    def convert(serialized_model_path: str, extended_unimodel_instructions: Dict[str, Callable[[UniLayerWildcard], UniLayer]] = None) -> UniModel:
        if not serialized_model_path.endswith(f"{UNIMODEL}.pb"):
            raise UniModelException(message=f"UniModel extension must be {UNIMODEL}.pb")
        if extended_unimodel_instructions is None:
            extended_unimodel_instructions = {}
        extended_unilayer_instructions_manager.set_custom_instructions(extended_unimodel_instructions)
        const_file = serialized_model_path[:-len(f"{UNIMODEL}.pb")] + UNIMODEL_CONST_EXT
        const_file_exists = False
        if os.path.isfile(const_file):
            const_compressor_holder.read_from_file(const_file)
            const_file_exists = True
        graphdef = GraphDefToUniModelConverter._load_model(serialized_model_path)
        unimodel_casted = GraphDefToUniModelConverter._cast_model(graphdef, const_file_exists)
        extended_unilayer_instructions_manager.clean_custom_instructions()
        return unimodel_casted

    @staticmethod
    def _load_model(serialized_model_path: str)-> GraphDef:
        # validate path
        if not os.path.exists(serialized_model_path):
            raise ValueError(f"{serialized_model_path} file is not found")

        # deserialize proto to graph def
        graph_def = GraphDef()
        with open(serialized_model_path, 'rb') as f:
            graph_def.ParseFromString(f.read())
        return graph_def

    @staticmethod
    def _cast_model(graphdef: GraphDef, const_file_exists: bool) -> UniModel:
        metadata = GraphDefToUniModelConverter._extract_model_metadata(graphdef)
        if out_const_saving_method_str in metadata and metadata[out_const_saving_method_str] == "true" and not const_file_exists:
            raise UniModelException(ErrorCodes.MCF, f"{ErrorCodes.MCF.value} for model")
        cast_model = UniModelGenerator.generate_model_without_validation(metadata)
        graph_ids = GraphDefToUniModelConverter._extract_graphs(graphdef, cast_model)
        [GraphDefToUniModelConverter._extract_graph_nodes(graphdef, cast_model, graph_id) for graph_id in graph_ids]
        const_compressor_holder.clean_data()
        return cast_model.build()


    @staticmethod
    def _extract_model_metadata(graph_def: GraphDef)-> Dict[str, str]:
        mode_prop_node = [n for n in graph_def.node if n.op == MODEL_DEF_OP][0]
        attr = AttrValueGenerator.extract_attr(mode_prop_node)
        metadata_prefix = f"{METADATA}-"
        return {k[len(metadata_prefix):]: v for k, v in attr.items() if k.startswith(metadata_prefix)}

    @staticmethod
    def _extract_graphs(graph_def: GraphDef, model: UniModelBuilder)->List[str]:
        graph_ids = []
        metadata_prefix = f"{METADATA}-"
        for g in graph_def.node:
            if g.op == NET_DEF_OP:
                attr= AttrValueGenerator.extract_attr(g)
                metadata = {k[len(metadata_prefix):]: v for k, v in attr.items() if k.startswith(metadata_prefix)}
                UniModelGenerator.generate_graph_in_model(model, attr[NAME_ATTR], attr[ID_ATTR], attr[ORDINAL], metadata=metadata)
                graph_ids.append(attr[ID_ATTR])
        return graph_ids

    @staticmethod
    def _extract_graph_nodes(graph: GraphDef, cast_model: UniModelBuilder, graph_id: str):
        generated_nodes = {}
        inputs_for_node = {}
        for node in graph.node:
            attr = AttrValueGenerator.extract_attr(node)
            if node.op not in [MODEL_DEF_OP, NET_DEF_OP] and attr[GRAPH_ID] == graph_id:
                new_node = node_to_uni_layer(node).decompact()
                UniModelGenerator.add_layer_to_graph_in_model(cast_model, graph_id, new_node)
                generated_nodes[node.name] = new_node
                inputs_for_node[node.name] = node.input

        for node_name, node in generated_nodes.items():
            for i in inputs_for_node[node_name]:
                regex = r":\d+:\d+$"
                match = re.search(regex, i)
                if match:
                    _, from_index, to_index = i[match.start(): match.end()].split(INPUT_SPLITTER)
                    from_node = i[0: match.start()]
                    UniModelGenerator.add_edge(cast_model, graph_id, generated_nodes[from_node], node,
                                                               int(from_index), int(to_index))


