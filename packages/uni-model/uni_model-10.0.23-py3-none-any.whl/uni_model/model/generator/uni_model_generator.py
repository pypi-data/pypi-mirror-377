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
from typing import Dict

from uni_model.model.uni_layer import UniLayer
from uni_model.model.uni_edge import UniEdge
from uni_model.model.uni_graph import UniGraphBuilder
from uni_model.model.uni_model import UniModel, UniModelBuilder
from uni_model.validation.validation_cfg import ValidationCfg, no_validation
from uni_model.validation.uni_model_exception import UniModelException


class UniModelGenerator:
    @staticmethod
    def generate_model(validation_cfg: ValidationCfg, metadata: Dict[str, str] = None) -> UniModelBuilder:
        if metadata is None:
            metadata = {}
        return UniModelBuilder(validation_cfg, metadata)

    @staticmethod
    def generate_model_without_validation(metadata: Dict[str, str] = None) -> UniModelBuilder:
        if metadata is None:
            metadata = {}
        return UniModelBuilder(ValidationCfg(False, no_validation), metadata)

    @staticmethod
    def generate_graph_in_model(model: UniModelBuilder, name: str, id: str, ordinal: int,
                                metadata: Dict[str, str] = None):
        if metadata is None:
            metadata = {}
        graph = UniGraphBuilder(model.validation_cfg, model.error_builder, name, id, ordinal, metadata=metadata)
        model.add_graph(graph)

    @staticmethod
    def add_layer_to_graph_in_model(model: UniModelBuilder, graph_id: str, layer: UniLayer):
        selected_graphs = [g for g in model.uni_graphs if g.id == graph_id]
        if len(selected_graphs) == 0:
            raise UniModelException(message="You cannot add a layer to non exiting graph")
        selected_graphs[0].add_layer_node(layer)

    @staticmethod
    def add_edge(model: UniModelBuilder, graph_id: str, from_node: UniLayer, to_node: UniLayer,
                 from_index: int, to_index: int):
        edge = UniEdge(from_node, from_index, to_node, to_index)
        selected_graphs = [g for g in model.uni_graphs if g.id == graph_id]
        if len(selected_graphs) == 0:
            raise UniModelException(message="You cannot add an edge to non exiting graph")
        selected_graphs[0].add_edge(edge)

    @staticmethod
    def build(model: UniModelBuilder) -> UniModel:
        return model.build()
