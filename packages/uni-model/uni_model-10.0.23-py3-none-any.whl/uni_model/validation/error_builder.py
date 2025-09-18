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
Created on 1/22/23

@author: zvikaa
'''
from typing import List

from uni_model.validation.error_report import ErrorReport


class ErrorBuilder:
    def __init__(self):
        self.error_list: List[ErrorReport] = []

    def log_error(self, error: ErrorReport):
        self.error_list.append(error)

    def is_valid_model(self):
        return len(self.error_list) == 0

    def get_errors(self):
        if len(self.error_list) > 0:
            errors_str = "\n".join([str(e) for e in self.error_list])
            return f"Error in building UniModel:\n{errors_str}"
        else:
            return ""

    def get_errors_as_report(self):
        return self.error_list


