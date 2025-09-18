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
Created on 8/10/23

@author: zvikaa
'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Any, Dict

from uni_model import UniLayer, UniGraph, UniModel


@dataclass
class NodeInGraph:
    node: UniLayer
    graph: UniGraph


class LinterRule(ABC):
    name: str
    explanation: str

    @abstractmethod
    def validate(self, element):
        raise NotImplementedError


class ModelLinterRule(LinterRule):
    @abstractmethod
    def validate(self, element: UniModel):
        raise NotImplementedError


class GraphLinterRule(LinterRule):
    @abstractmethod
    def validate(self, element: UniGraph):
        raise NotImplementedError


class NodeLinterRule(LinterRule):
    @abstractmethod
    def validate(self, element: UniLayer):
        raise NotImplementedError


@dataclass
class LinterResult:
    rule_name: str
    element: Any
    explanation: str


@dataclass
class LinterReport:
    model_report: List[LinterResult]
    graph_report: Dict[str, List[LinterResult]]
    node_report: Dict[str, Dict[str, List[LinterResult]]]


class Linter:
    def __init__(self, linter_rules: List[LinterRule]):
        self.linter_rules = linter_rules

    def _lint_model(self, model: UniModel) -> List[LinterResult]:
        model_results = []
        model_rules = [rule for rule in self.linter_rules if isinstance(rule, ModelLinterRule)]
        for model_rule in model_rules:
            if not model_rule.validate(model):
                model_results.append(LinterResult(model_rule.name, model, model_rule.explanation))
        return model_results

    def _lint_graphs(self, model: UniModel) -> Dict[str, List[LinterResult]]:
        graph_results = {}
        graph_rules = [rule for rule in self.linter_rules if isinstance(rule, GraphLinterRule)]
        for rule in graph_rules:
            for graph in model.uni_graphs:
                if not rule.validate(graph):
                    if graph.id not in graph_results:
                        graph_results[graph.id] = []
                    graph_results[graph.id].append(LinterResult(rule.name, graph, rule.explanation))
        return graph_results

    def _lint_nodes(self, model: UniModel) -> Dict[str, Dict[str, List[LinterResult]]]:
        nodes_results = {}
        nodes_rules = [rule for rule in self.linter_rules if isinstance(rule, NodeLinterRule)]
        for rule in nodes_rules:
            for graph in model.uni_graphs:
                for node in graph.layer_nodes:
                    if not rule.validate(NodeInGraph(node, graph)):
                        if graph.id not in nodes_results:
                            nodes_results[graph.id] = {}
                        if node.name not in nodes_results[graph.id]:
                            nodes_results[graph.id][node.name] = []
                        nodes_results[graph.id][node.name].append(LinterResult(rule.name, node, rule.explanation))
        return nodes_results

    def lint(self, model: UniModel) -> LinterReport:
        return LinterReport(self._lint_model(model), self._lint_graphs(model), self._lint_nodes(model))
