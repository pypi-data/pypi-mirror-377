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

from dataclasses import dataclass, field

import numpy as np

from uni_model.model.quantization.Qtype import Qtype
from typing import List
from uni_model.validation.error_codes import ErrorCodes
from uni_model.validation.uni_model_exception import UniModelException
from uni_model.validation.validation_cfg import ValidationCfg, ReportForValidationViolation
from uni_model.validation.error_builder import ErrorBuilder
from uni_model.validation.error_report import ErrorReport


@dataclass(frozen=True)
class Lut(Qtype):
	table: List[float] 
	table_n_bits: int # size of lut, usually 2 or 4
	normalized_min: float
	normalized_max: float
	_table_as_np: np.ndarray = field(default=None, init=False, repr=False)

	def __post_init__(self):
		if len(self.table) > 2 ** self.table_n_bits and self.table_n_bits != 0:
			raise UniModelException(ErrorCodes.LTSR, f"{ErrorCodes.LTSR.value} but is {len(self.table)}")
		object.__setattr__(self, '_table_as_np', np.array(self.table, dtype=np.float32))
		if np.any(self._table_as_np < self.normalized_min) or np.any(self._table_as_np > self.normalized_max):
			raise UniModelException(ErrorCodes.LNVMMIR, f"{ErrorCodes.LNVMMIR.value}")


	def validate(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, graph_id: str, layer):
		if validation_cfg.validation_for_violation.require_zero_in_lut_table:
			if 0 not in self.table and len(self.table) == 2**self.table_n_bits:
				error_builder.log_error(ErrorReport(ReportForValidationViolation.ZIL, graph_id, layer.name, layer.op))


