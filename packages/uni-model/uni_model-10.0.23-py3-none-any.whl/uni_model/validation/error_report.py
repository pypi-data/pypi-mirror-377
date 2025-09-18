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
Created on 2/22/23

@author: zvikaa
'''
from dataclasses import dataclass

from uni_model.validation.validation_cfg import ReportForValidationViolation, GraphElementForReport


@dataclass()
class ErrorReport:
    report: ReportForValidationViolation
    graph_id: str = None
    layer_name: str = None
    op: str = None
    edge_desc: str = None
    extra_information: str = ""

    def __post_init__(self):
        if self.report.value.element == GraphElementForReport.GRAPH:
            assert self.graph_id is not None
        if self.report.value.element == GraphElementForReport.NODE:
            assert self.layer_name is not None and self.graph_id is not None and self.op is not None
        if self.report.value.element == GraphElementForReport.EDGE:
            assert self.edge_desc is not None and self.graph_id is not None

    def __str__(self):
        if self.report.value.element == GraphElementForReport.MODEL:
            return f"In model: {self.report.value.desc} {self.extra_information}"
        elif self.report.value.element == GraphElementForReport.GRAPH:
            return f"In graph {self.graph_id}: ${self.report.value.desc} {self.extra_information}"
        elif self.report.value.element == GraphElementForReport.NODE:
            return f"In node {self.layer_name} with op {self.op} in graph {self.graph_id}: ${self.report.value.desc} {self.extra_information}"
        elif self.report.value.element == GraphElementForReport.EDGE:
            return f"In edge {self.edge_desc} in graph {self.graph_id}: ${self.report.value.desc} {self.extra_information}"