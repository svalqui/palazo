from collections.abc import MutableMapping
from collections import OrderedDict as default_dict, ChainMap as _ChainMap
import functools
import io
import itertools
import os
import re
import sys
import warnings


def _read(self, file_handle, ):


def read_file(self, file_name, encoding=None):
    try:
        with open(file_name, encoding=encoding) as file_handle:
            self._read(file_handle, file_name)

        self._read(file_handle)
