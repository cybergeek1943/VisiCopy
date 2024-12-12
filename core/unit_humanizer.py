# TODO review

def format_seconds(s: int) -> str:
    """Converts integer seconds into string of hour:minute:second
    >>> format_seconds(45)
    '45s'
    >>> format_seconds(1000)
    '16m:40s'
    >>> format_seconds(0)
    '0s'
    >>> format_seconds(10000)
    '2h:46m:40s'
    """
    m = s // 60
    h = m // 60
    return f'{h}h:{m-(h*60)}m:{s-(m*60)}s' if h> 0 else (f'{m}m:{s-(m*60)}s' if m>0 else f'{s}s')

def format_bytes(b: int, per_second: bool = False) -> str:
    """Converts integer bytes into strings
    >>> format_bytes(0, True)
    '0Bps'
    >>> format_bytes(1200, True)
    '1.17KBps'
    >>> format_bytes(9999999, False)
    '9.54MB'
    >>> format_bytes(1234567890, False)
    '1.15GB'
    """
    time: str = 'ps' if per_second else ''
    if b >= 1024:
        if b >= (mb_divisor:=1024*1024):
            if b>= (gb_divisor:=1024*1024*1024):
                return f'{round(b / (gb_divisor), 2)}GB{time}'
            return f'{round(b / (mb_divisor), 2)}MB{time}'
        return f'{round(b / 1024, 2)}KB{time}'
    return f'{b}B{time}'

if __name__ == '__main__':
    print(format_bytes(654342, per_second=True))
