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
