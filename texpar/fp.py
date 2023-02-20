# Copyright 2019-2023 by Sergio Valqui. All rights reserved.

from collections.abc import MutableMapping
from collections import OrderedDict as default_dict, ChainMap as _ChainMap
import functools
import io
import itertools
import os
import re
import sys
import warnings


def _read(self, file_handle):
    for line in file_handle:
        print()


def read_file(self, file_name, encoding=None):
    try:
        with open(file_name, encoding=encoding) as file_handle:
            self._read(file_handle)
    self._read(file_name)



    # read(filenames, encoding=None)
    # read_file(f, filename=None)
    # metainfo()
    # metainfo.keys(), list of keys
    # metainfo.key.values(), list of values per key
    # fileformat() same or warning
    # data.header()
    # columns_detailed()
    # columns_details()
    # data.CHROM(), list of CHROMs
    # data.CHROM.POS, list of POSs
    # data.CHROM.POS.data_raw(), always text as found in the file
    # data.CHROM.POS.data, formatted as specified in the column_details
