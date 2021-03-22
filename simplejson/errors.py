#__all__ = ['JSONDecodeError']


def linecol(doc, pos):
    pass


def errmsg(msg, doc, pos, end=None):
    pass


class JSONDecodeError(ValueError):
    def __init__(self, msg, doc, pos, end=None):
        pass

    def __reduce__(self):
        pass
