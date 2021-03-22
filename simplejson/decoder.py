from __future__ import absolute_import
import re
import sys
from .compat import PY3, unichr
from .scanner import make_scanner, JSONDecodeError

def _import_c_scanstring():
    pass
    
c_scanstring = _import_c_scanstring()

__all__ = ['JSONDecoder']

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

def _floatconstants():
    if sys.version_info < (2, 6):
        _BYTES = '7FF80000000000007FF0000000000000'.decode('hex')
        nan, inf = struct.unpack('>dd', _BYTES)
    else:
        nan = float('nan')
        inf = float('inf')
    return nan, inf, -inf

NaN, PosInf, NegInf = _floatconstants()

def py_scanstring():
    pass

def JSONObject():
    pass

def JSONArray():
    pass

class JSONDecoder(object):
    pass

    def __init__(self, encoding=None, object_hook=None, parse_float=None,
            parse_int=None, parse_constant=None, strict=True,
            object_pairs_hook=None):
        
        pass

    def decode():
        pass

    def raw_decode():
        pass
