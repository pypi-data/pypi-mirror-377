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
Created on 1/17/23

@author: zvikaa
'''
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class ValidationCfgForViolations:
    require_unique_graph_ordinal: bool = True
    require_out_q_info_equals_output_size: bool = True
    require_unique_to_indices_in_edge: bool = True
    require_input_match_to_input_size: bool = True
    require_successive_input_indices: bool = True
    require_legal_shape_in_reshape: bool = True
    require_connected_graph: bool = True
    require_zero_in_lut_table: bool = False
    require_match_qtype_and_shapes: bool = True
    require_accuracy_in_const_fixed_point_repr: bool = False


@dataclass
class ValidationCfg:
    throw_errors_as_expected: bool = True
    validation_for_violation: ValidationCfgForViolations = field(default_factory=ValidationCfgForViolations)


no_validation = ValidationCfgForViolations(
    require_unique_graph_ordinal=False,
    require_out_q_info_equals_output_size=False,
    require_unique_to_indices_in_edge=False,
    require_input_match_to_input_size=False,
    require_successive_input_indices=False,
    require_legal_shape_in_reshape=False,
    require_connected_graph=False,
    require_zero_in_lut_table=False,
    require_match_qtype_and_shapes = False,
    require_accuracy_in_const_fixed_point_repr = False
)


class GraphElementForReport(Enum):
    MODEL = 0
    GRAPH = 1
    NODE = 2
    EDGE = 3


@dataclass
class ReportInformation:
    desc: str
    element: GraphElementForReport


class ReportForValidationViolation(Enum):
    UGO = ReportInformation("Unique graph ordinal is violated", GraphElementForReport.MODEL)
    OQIEOS = ReportInformation("OutQInfo size must be in range of valid output range", GraphElementForReport.NODE)
    UTIIE = ReportInformation("In edges that share to-node, each index must be unique", GraphElementForReport.NODE)
    IMTIS = ReportInformation("Size of inputs must be in valid input range", GraphElementForReport.NODE)
    SII = ReportInformation("Input indices in edges must be successive", GraphElementForReport.NODE)
    LSIRS = ReportInformation("Shape in reshape layer can have only one occurrence of -1 and no non-positive values",
                              GraphElementForReport.NODE)
    CG = ReportInformation("Nodes are not connected to any node in the graph", GraphElementForReport.GRAPH)
    ZIL = ReportInformation("Lut must contain value 0 or must keep space for it", GraphElementForReport.NODE)
    QTMMS = ReportInformation("Qtypes must match shapes data", GraphElementForReport.NODE)
