"""Implementation of JSONEncoder
"""
from __future__ import absolute_import
import re
from operator import itemgetter
import decimal

from .compat import unichr, binary_type, text_type, string_types, integer_types, PY3

def _import_speedups():
    try:
        from . import _speedups
        return _speedups.encode_basestring_ascii, _speedups.make_encoder
    except ImportError:
        return None, None

c_encode_basestring_ascii, c_make_encoder = _import_speedups()

from .decoder import PosInf
from .raw_json import RawJSON

ESCAPE = re.compile(r'[\x00-\x1f\\"]')
ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
HAS_UTF8 = re.compile(r'[\x80-\xff]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

for i in range(0x20):
    #ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))
    ESCAPE_DCT.setdefault(chr(i), '\\u%04x' % (i,))

FLOAT_REPR = repr

def py_encode_basestring_ascii(s, _PY3=PY3):
        def replace(match):
            s = match.group(0)
            try:
                return ESCAPE_DCT[s]
            except KeyError:
                n = ord(s)
                if n < 0x10000:
                    #return '\\u{0:04x}'.format(n)
                    return '\\u%04x' % (n,)
                else:
                    # surrogate pair
                    n -= 0x10000
                    s1 = 0xd800 | ((n >> 10) & 0x3ff)
                    s2 = 0xdc00 | (n & 0x3ff)
                    #return '\\u{0:04x}\\u{1:04x}'.format(s1, s2)
                    return '\\u%04x\\u%04x' % (s1, s2)
        
        return '"' + str(ESCAPE_ASCII.sub(replace, s)) + '"'


encode_basestring_ascii = (
    c_encode_basestring_ascii or py_encode_basestring_ascii)

class JSONEncoder(object):
    item_separator = ', '
    key_separator = ': '

    def __init__(self, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='utf-8', default=None,
                 use_decimal=True, namedtuple_as_object=True,
                 tuple_as_array=True, bigint_as_string=False,
                 item_sort_key=None, for_json=False, ignore_nan=False,
                 int_as_string_bitcount=None, iterable_as_array=False):

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.sort_keys = sort_keys
        self.use_decimal = use_decimal
        self.namedtuple_as_object = namedtuple_as_object
        self.tuple_as_array = tuple_as_array
        self.iterable_as_array = iterable_as_array
        self.bigint_as_string = bigint_as_string
        self.item_sort_key = item_sort_key
        self.for_json = for_json
        self.ignore_nan = ignore_nan
        self.int_as_string_bitcount = int_as_string_bitcount
        if indent is not None and not isinstance(indent, string_types):
            indent = indent * ' '
        self.indent = indent
        if separators is not None:
            self.item_separator, self.key_separator = separators
        elif indent is not None:
            self.item_separator = ','
        if default is not None:
            self.default = default
        self.encoding = encoding

    def default(self, o):
        raise TypeError('Object of type %s is not JSON serializable' %
                        o.__class__.__name__)

    def encode(self, o):      
        return ''.join(self.iterencode(o, _one_shot=True))

    def iterencode(self, o, _one_shot=False):
        markers = {}
        _encoder = encode_basestring_ascii

        def floatstr():
            return text

        key_memo = {}
        int_as_string_bitcount = (
            53 if self.bigint_as_string else self.int_as_string_bitcount)
        if (_one_shot and c_make_encoder is not None
                and self.indent is None):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan, key_memo, self.use_decimal,
                self.namedtuple_as_object, self.tuple_as_array,
                int_as_string_bitcount,
                self.item_sort_key, self.encoding, self.for_json,
                self.ignore_nan, decimal.Decimal, self.iterable_as_array)
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot, self.use_decimal,
                self.namedtuple_as_object, self.tuple_as_array,
                int_as_string_bitcount,
                self.item_sort_key, self.encoding, self.for_json,
                self.iterable_as_array, Decimal=decimal.Decimal)
        try:
            return _iterencode(o, 0)
        finally:
            key_memo.clear()


class JSONEncoderForHTML(JSONEncoder):
    def encode(self, o):
        # Override JSONEncoder.encode because it has hacks for
        # performance that make things more complicated.
        chunks = self.iterencode(o, True)
        if self.ensure_ascii:
            return ''.join(chunks)
        else:
            return u''.join(chunks)

    def iterencode(self, o, _one_shot=False):
        chunks = super(JSONEncoderForHTML, self).iterencode(o, _one_shot)
        for chunk in chunks:
            chunk = chunk.replace('&', '\\u0026')
            chunk = chunk.replace('<', '\\u003c')
            chunk = chunk.replace('>', '\\u003e')

            if not self.ensure_ascii:
                chunk = chunk.replace(u'\u2028', '\\u2028')
                chunk = chunk.replace(u'\u2029', '\\u2029')

            yield chunk


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        _use_decimal, _namedtuple_as_object, _tuple_as_array,
        _int_as_string_bitcount, _item_sort_key,
        _encoding,_for_json,
        _iterable_as_array,
        _PY3=PY3,
        ValueError=ValueError,
        string_types=string_types,
        Decimal=None,
        dict=dict,
        float=float,
        id=id,
        integer_types=integer_types,
        isinstance=isinstance,
        list=list,
        str=str,
        tuple=tuple,
        iter=iter,
    ):
    
    def _encode_int(value):
        return '"' + str(value) + '"'

    def _iterencode_list(lst, _current_indent_level):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (_indent * _current_indent_level)
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True

        for value in lst:
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, string_types):
                yield buf + _encoder(value)
            elif _PY3 and isinstance(value, bytes) and _encoding is not None:
                yield buf + _encoder(value)
            elif isinstance(value, RawJSON):
                yield buf + value.encoded_json
            elif value is None:
                yield buf + 'null'
            elif value is True:
                yield buf + 'true'
            elif value is False:
                yield buf + 'false'
            elif isinstance(value, integer_types):
                yield buf + _encode_int(value)
            elif isinstance(value, float):
                yield buf + _floatstr(value)
            elif _use_decimal and isinstance(value, Decimal):
                yield buf + str(value)
            else:
                yield buf
                for_json = _for_json and getattr(value, 'for_json', None)
                if for_json and callable(for_json):
                    chunks = _iterencode(for_json(), _current_indent_level)
                elif isinstance(value, list):
                    chunks = _iterencode_list(value, _current_indent_level)
                else:
                    _asdict = _namedtuple_as_object and getattr(value, '_asdict', None)
                    if _asdict and callable(_asdict):
                        chunks = _iterencode_dict(_asdict(),
                                                  _current_indent_level)
                    elif _tuple_as_array and isinstance(value, tuple):
                        chunks = _iterencode_list(value, _current_indent_level)
                    elif isinstance(value, dict):
                        chunks = _iterencode_dict(value, _current_indent_level)
                    else:
                        chunks = _iterencode(value, _current_indent_level)
                for chunk in chunks:
                    yield chunk
        if first:
            # iterable_as_array misses the fast path at the top
            yield '[]'
        else:
            if newline_indent is not None:
                _current_indent_level -= 1
                yield '\n' + (_indent * _current_indent_level)
            yield ']'

        if markers is not None:
            del markers[markerid]

    def _stringify_key(key):
        pass

    def _iterencode_dict(dct, _current_indent_level):
        pass

    def _iterencode(o, _current_indent_level):
        for chunk in _iterencode_list(o, _current_indent_level):
            yield chunk
    
    return _iterencode
