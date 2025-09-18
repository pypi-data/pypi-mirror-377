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

from typing import List, Dict, Set
import itertools
from uni_model.utils.immute import immute
from uni_model.model.uni_edge import UniEdge, UniEdgeKey
from uni_model.model.uni_layer import UniLayer
from uni_model.validation.error_builder import ErrorBuilder
from uni_model.validation.error_codes import ErrorCodes
from uni_model.validation.error_report import ErrorReport
from uni_model.validation.validation_cfg import ValidationCfg, ReportForValidationViolation
import networkx as nx

from uni_model.validation.uni_model_exception import UniModelException


class UniGraphBuilder:
    def __init__(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, name: str, id: str, ordinal: int,
                 layer_nodes: Dict[str, UniLayer] = None, uni_edges: Dict[UniEdgeKey, UniEdge] = None,
                 metadata: Dict[str, str] = None):
        if uni_edges is None:
            uni_edges = {}
        if layer_nodes is None:
            layer_nodes = {}
        if metadata is None:
            metadata = {}
        # both id and name is needed since we may have 2 similar networks with the same name, but the only way to
        # differentiate them is by id
        self.name = name
        self.id = id
        self.ordinal = ordinal
        self.layer_nodes = layer_nodes
        self.edges = uni_edges
        self.validation_cfg = validation_cfg
        self.error_builder = error_builder
        self.metadata = metadata

    def add_layer_node(self, node: UniLayer):
        if node.name in self.layer_nodes:
            if node != self.layer_nodes[node.name]:
                raise UniModelException(ErrorCodes.LNMBU, f"Node named {node.name} in graph {self.name}: {ErrorCodes.LNMBU.value}")

        self.layer_nodes[node.name] = node

    def add_edge(self, edge: UniEdge):
        # edge in graph must be unique
        if edge.to_key() in self.edges:
            raise UniModelException(ErrorCodes.EMBU, f"Edge {edge.desc()} in graph {self.name}: {ErrorCodes.EMBU.value}")
        # nodes in edge must be in graph before addition
        if edge.from_node.name not in self.layer_nodes:
            raise UniModelException(ErrorCodes.ENMBIG, f"Node {edge.from_node.name} in graph {self.name}: {ErrorCodes.ENMBIG.value}")
        if edge.to_node.name not in self.layer_nodes:
            raise UniModelException(ErrorCodes.ENMBIG, f"Node {edge.to_node.name} in graph {self.name}: {ErrorCodes.ENMBIG.value}")
        self.edges[edge.to_key()] = edge

    def build(self):
        self.validate_graph()
        return UniGraph(self)

    def validate_graph(self):
        for node in self.layer_nodes.values():
            node.validate(self.validation_cfg, self.error_builder, self.id)

        edges_value = list(self.edges.values())
        edges_value.sort(key=lambda x: x.to_node.name)
        layer_input = {k: list(v) for k, v in
                       itertools.groupby(edges_value, lambda x: x.to_node)}

        if self.validation_cfg.validation_for_violation.require_unique_to_indices_in_edge:
            # each node A cannot have in indices (by edges) that are used more than once.
            # For example, see in validation test
            edges_value = list(self.edges.values())
            edges_value.sort(key=lambda x: x.to_node.name)

            for node, edge_list in layer_input.items():
                edge_list.sort(key=lambda x: x.to_index)
                edges_for_index = {k: list(v) for k, v in itertools.groupby(edge_list, lambda x: x.to_index)}
                illegal_indices = [edge_to_index for edge_to_index, values in edges_for_index.items() if
                                   len(list(values)) > 1]
                if len(illegal_indices) > 0:
                    self.error_builder.log_error(ErrorReport(ReportForValidationViolation.UTIIE, graph_id = self.id,
                                                             layer_name = node.name, op=node.op))

        if self.validation_cfg.validation_for_violation.require_successive_input_indices:
            # in node A, all indices through edges must be successive with no skipping
            for node, edge_list in layer_input.items():
                indices = [e.to_index for e in edge_list]
                if set(indices) != set(range(len(indices))):
                    self.error_builder.log_error(ErrorReport(ReportForValidationViolation.SII, graph_id = self.id,
                                                             layer_name = node.name, op=node.op))

        if self.validation_cfg.validation_for_violation.require_input_match_to_input_size:
            # in each node, size if input is declared as a range. All in edges size must be in this range
            for node in self.layer_nodes.values():
                if layer_input.get(node) is not None and len(
                        layer_input.get(node)) not in node.valid_input_range:
                    self.error_builder.log_error(
                        ErrorReport(ReportForValidationViolation.IMTIS, graph_id = self.id, layer_name = node.name, op=node.op,
                                    extra_information = f"Layer op {node.op} has valid input range of {node.valid_input_range}"))

        if self.validation_cfg.validation_for_violation.require_connected_graph:
            # graph must be connected
            connected_nodes = set([e.from_node.name for e in self.edges.values()] + [e.to_node.name for e in self.edges.values()])
            nodes_as_set = set([n.name for n in self.layer_nodes.values()])
            disconnected_nodes = nodes_as_set - connected_nodes
            if len(disconnected_nodes) > 0:
                self.error_builder.log_error(
                    ErrorReport(ReportForValidationViolation.CG, graph_id = self.id, layer_name = ",".join(disconnected_nodes)))


class UniGraph:
    def __init__(self, graph: UniGraphBuilder):
        self.name = graph.name
        self.id = graph.id
        self.ordinal = graph.ordinal
        self.metadata = graph.metadata
        DG = nx.DiGraph()
        DG.add_nodes_from(graph.layer_nodes.keys())
        DG.add_edges_from([(e.from_node.name, e.to_node.name) for e in graph.edges.values()])
        self.layer_nodes = []
        self.edges = []
        sorted_graph = nx.lexicographical_topological_sort(DG)
        for n in sorted_graph:
            self.layer_nodes.append(graph.layer_nodes[n])
            for el in sorted([e for e in graph.edges.values() if e.from_node.name == n], key = lambda x: (x.to_node.name, x.from_index, x.to_index)):
                self.edges.append(el)

    def __eq__(self, other):
        if not isinstance(other, UniGraph):
            return False
        if self.name != other.name or self.id != other.id or self.ordinal != other.ordinal or \
                self.layer_nodes != other.layer_nodes or\
                self.edges != other.edges or self.metadata!=other.metadata:
            return False
        return True

    def __hash__(self):
        return hash((self.name, self.id, self.ordinal, tuple(self.layer_nodes), tuple(self.edges), immute(self.metadata)))
