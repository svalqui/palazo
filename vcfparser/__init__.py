##  ConfigParser used as reference

from collections.abc import MutableMapping
from collections import OrderedDict as _default_dict, ChainMap as _ChainMap
import functools
import io
import itertools
import re
import sys
import warnings
from Bio import SeqIO

class BaseParser(MutableMapping):
    """ """

    # Regular expressions for parsing section headers and options
