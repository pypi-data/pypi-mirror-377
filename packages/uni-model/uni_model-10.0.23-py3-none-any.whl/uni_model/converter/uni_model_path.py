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
Created on 3/14/23

@author: zvikaa
'''
from dataclasses import dataclass

from uni_model.converter.const_list import UNIMODEL, UNIMODEL_CONST_EXT
from uni_model.validation.uni_model_exception import UniModelException


@dataclass()
class UniModelPath:
    directory: str
    file_name_without_extension: str
    txt_format: bool = False

    def __post_init__(self):
        if self.directory == "" or self.file_name_without_extension == "":
            raise UniModelException(message="Directory and filename must have content")

    def to_absolute_file_name(self) -> str:
        if self.txt_format:
            return f"{self.directory}/{self.file_name_without_extension}.{UNIMODEL}.pbtxt"
        else:
            return f"{self.directory}/{self.file_name_without_extension}.{UNIMODEL}.pb"

    def to_const_file(self)->str:
        return f"{self.directory}/{self.file_name_without_extension}.{UNIMODEL_CONST_EXT}"

    @staticmethod
    def path_to_uni_model_path(path: str):
        path_split = path.split("/")
        directory = "/".join(path_split[:-1])
        filename = ".".join(path_split[-1].split(".")[:-2])
        txt_format = path_split[-1].split(".")[-1] == "pbtxt"
        return UniModelPath(directory=directory, file_name_without_extension=filename, txt_format=txt_format)


class UniModelFileNameAssistant:
    @classmethod
    def generate_uni_model_path(cls, directory: str, identifier: str, component_name: str,
                                txt_format: bool = False) -> UniModelPath:
        return UniModelPath(directory, f"{identifier}.{component_name}", txt_format)

    @classmethod
    def replace_component(cls, path_to_uni_model: str, new_component: str)-> UniModelPath:
        if path_to_uni_model == "" or new_component == "":
            raise UniModelException(message="path or component name have to be not empty")
        current_uni_model_path = UniModelPath.path_to_uni_model_path(path_to_uni_model)
        new_file_name = ".".join(current_uni_model_path.file_name_without_extension.split(".")[:-1] + [new_component])
        return UniModelPath(current_uni_model_path.directory, new_file_name, current_uni_model_path.txt_format)

    @classmethod
    def extract_component(cls, path_to_uni_model: str) -> str:
        current_uni_model_path = UniModelPath.path_to_uni_model_path(path_to_uni_model)
        component_split = current_uni_model_path.file_name_without_extension.split(".")
        if len(component_split) == 1:
            return ""
        else:
            return component_split[-1]


