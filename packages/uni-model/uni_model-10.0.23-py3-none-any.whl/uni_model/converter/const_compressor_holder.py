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
Created on 7/3/23

@author: zvikaa
'''
from typing import List
import struct

import numpy as np


class ConstCompressorHolder:
    data_compress_to_write = []
    data_compress_to_read = b''
    overall_size = 0

    @staticmethod
    def nbits_to_bytes(n_bits: int) -> int:
        if n_bits in [2, 4, 8]:
            return 1
        elif n_bits == 16:
            return 2
        elif n_bits == 32:
            return 4
        else:
            raise Exception("Unsupported nbits")

    @staticmethod
    def nbits_to_struct_size_definition(n_bits: int) -> str:
        # struct_size_definition
        if n_bits in [2, 4, 8]:
            return "B"
        elif n_bits == 16:
            return "H"
        elif n_bits == 32:
            return "I"
        else:
            raise Exception("Unsupported nbits")

    def has_const_to_save(self) -> bool:
        return len(self.data_compress_to_write) > 0

    def has_const_to_read(self) -> bool:
        return len(self.data_compress_to_read) > 0

    def hold_const_float_data(self, data: List[float]) -> range:
        if len(data) == 0:
            return range(0, 0)
        size_of_output = len(data)
        bytes_repr = struct.pack(">" + "f" * size_of_output, *data)
        return self._inner_hold(bytes_repr)

    def hold_const_fixed_point_repr(self, data: List[int], n_bits: int) -> range:
        if len(data) == 0:
            return range(0, 0)
        struct_size_definition = ConstCompressorHolder.nbits_to_struct_size_definition(n_bits)
        size_of_output = len(data)
        bytes_repr = struct.pack(">" + struct_size_definition * size_of_output, *data)
        return self._inner_hold(bytes_repr)

    def _inner_hold(self, byte_repr: bytes) -> range:
        self.data_compress_to_write.append(byte_repr)
        begin = self.overall_size
        end = begin + len(byte_repr)
        self.overall_size = end
        return range(begin, end)

    def read_const_float_data(self, range_of_data: range) -> List[float]:
        data = self.data_compress_to_read[range_of_data.start:range_of_data.stop]
        return_value = list(struct.unpack(">" + "f" * (len(data) // 4), data))
        return return_value

    def read_const_fixed_point_repr(self, range_of_data: range, n_bits: int) -> List[int]:
        data = self.data_compress_to_read[range_of_data.start:range_of_data.stop]
        struct_size_definition = ConstCompressorHolder.nbits_to_struct_size_definition(n_bits)
        bytes_size = ConstCompressorHolder.nbits_to_bytes(n_bits)
        return_value = list(struct.unpack(">" + struct_size_definition * (len(data) // bytes_size), data))
        return return_value

    def save_to_file(self, const_file_path: str):
        with open(const_file_path, 'wb') as const_file:
            for member in self.data_compress_to_write:
                const_file.write(member)
                self.overall_size = 0

    def read_from_file(self, const_file_path: str):
        with open(const_file_path, 'rb') as const_file:
            self.data_compress_to_read = const_file.read()

    def clean_data(self):
        self.data_compress_to_read = b''
        self.overall_size = 0
        self.data_compress_to_write = []


const_compressor_holder = ConstCompressorHolder()
