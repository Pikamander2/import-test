import sys
from io import StringIO, BytesIO

PY3 = True
from importlib import reload as reload_module

def b(s):
    return bytes(s, 'latin1')

text_type = str
binary_type = bytes
string_types = (str,)
integer_types = (int,)
unichr = chr
