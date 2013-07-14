""":mod:`libfeedly.compat`
~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys

__all__ = 'PY3', 'urlparse', 'quote_plus', 'text', 'dict_iter', 'xlist'

PY3 = sys.version_info >= (3,)
if PY3:
    from urllib.parse import urlparse, quote_plus
else:
    from urlparse import urlparse
    from urllib import quote_plus

def text(string):
    if PY3 and isinstance(string, bytes):
        return string.decode()
    return string

def dict_iter(dict):
    if PY3:
        return dict.items()
    return dict.iteritems()

def xlist(collection):
    if isinstance(collection, list):
        return collection
    return list(collection)
