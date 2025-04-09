

ESCAPE_CHARS= [
    ('&#44;', ','),
    ('&#91;', '['),
    ('&#93;', ']'),
    ('&amp;', '&'),
]


def escape(s: str) -> str:
    if not isinstance(s, str): # type: ignore
        return s
    for e, o in ESCAPE_CHARS:
        s = s.replace(o, e)
    return s

def unescape(s: str) -> str:
    if not isinstance(s, str): # type: ignore
        return s
    for e, o in ESCAPE_CHARS:
        s = s.replace(e, o)
    return s

