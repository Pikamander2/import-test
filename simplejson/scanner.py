import re
from .errors import JSONDecodeError

def _import_c_make_scanner():
    try:
        from ._speedups import make_scanner
        return make_scanner
    except ImportError:
        return None

c_make_scanner = _import_c_make_scanner()

__all__ = ['make_scanner', 'JSONDecodeError']

def py_make_scanner(context):
    pass

make_scanner = c_make_scanner or py_make_scanner
