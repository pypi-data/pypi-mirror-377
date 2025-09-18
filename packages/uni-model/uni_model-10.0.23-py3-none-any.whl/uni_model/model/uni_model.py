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

from typing import List, Dict

from uni_model.model.uni_graph import UniGraphBuilder
from uni_model.utils.immute import immute
from uni_model.validation.error_builder import ErrorBuilder
from uni_model.validation.error_codes import ErrorCodes
from uni_model.validation.error_report import ErrorReport
from uni_model.validation.validation_cfg import ValidationCfg, ReportForValidationViolation
from uni_model.validation.uni_model_exception import UniModelException


class UniModelBuilder:
    def __init__(self, validation_cfg: ValidationCfg, metadata: Dict[str, str]):
        self.uni_graphs = []
        self.validation_cfg = validation_cfg
        self.error_builder = ErrorBuilder()
        self.graph_ids = set()
        self.metadata = metadata

    def add_graph(self, graph: UniGraphBuilder):
        if graph.id in self.graph_ids:
            raise UniModelException(ErrorCodes.GIMBU, f"Graph id {graph.id} {ErrorCodes.GIMBU.value}")
        self.uni_graphs.append(graph)
        self.graph_ids.add(graph.id)

    def validate(self):
        if self.validation_cfg.validation_for_violation.require_unique_graph_ordinal:
            ordinals = [g.ordinal for g in self.uni_graphs]
            if len(set(ordinals)) != len(ordinals):
                self.error_builder.log_error(ErrorReport(ReportForValidationViolation.UGO, extra_information= f"Given ordinals are {ordinals}."))

    def build(self):
        self.validate()
        model = UniModel(self, self.error_builder.get_errors_as_report())
        if self.validation_cfg.throw_errors_as_expected and not self.error_builder.is_valid_model():
            raise UniModelException(message=self.error_builder.get_errors())
        return model


class UniModel:
    def __init__(self, model_builder: UniModelBuilder, error_reports: List[ErrorReport]):
        self.uni_graphs = [ug.build() for ug in model_builder.uni_graphs]
        self.error_reports = error_reports
        self.metadata = model_builder.metadata

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, UniModel):
            return False
        if self.uni_graphs != other.uni_graphs or self.metadata != other.metadata:
            return False
        return True

    def __hash__(self):
        return hash((tuple(self.uni_graphs), immute(self.metadata)))

    def add_metadata_entry(self, key: str, value: str):
        self.metadata[key] = value
