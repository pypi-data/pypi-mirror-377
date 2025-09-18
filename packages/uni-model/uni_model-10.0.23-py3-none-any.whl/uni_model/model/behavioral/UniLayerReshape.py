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

from dataclasses import dataclass

from uni_model.auto_generated.UniLayerReshapeStructure import UniLayerReshapeStructure
from uni_model.validation.validation_cfg import ValidationCfg
from uni_model.validation.error_builder import ErrorBuilder

@dataclass(frozen=True, eq=False)
class UniLayerReshape(UniLayerReshapeStructure):

	def validate(self, validation_cfg: ValidationCfg, error_builder: ErrorBuilder, graph_id: str):
		super().validate(validation_cfg, error_builder, graph_id)
		self.validate_shape_in_reshape(validation_cfg, error_builder, self.shape, graph_id)


