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

    # Might need to be a handler/Mapper; handle records, map header

    # Regular expressions for parsing section headers and options

    # Header definition
    # Header parts, index to value, dictionary.

    # body/content definition

    # Section definition, one or more lines with an identifiable separator
    # Section parts, index to value, dictionary.

    # record header, known/defined content/headers, column like definition
    #   optional

    # record definition, one or more lines of repetitive content, known record header
    #   identifiable separator, row like.

    # multi value part, section/record value with identifiable separator, list like.

    # Opening file

    # content compliance

    # Error handling

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
