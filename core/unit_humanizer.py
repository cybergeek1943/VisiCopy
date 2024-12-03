# TODO add doctests and maybe improve design


def format_seconds(s: int) -> str:
    if s < 60:
        return f'{s}s'
    m: int = s // 60
    if m < 60:
        return f'{m}m:{s-(m*60)}s'
    h: int = m // 60
    return f'{h}h:{m-(h*60)}m:{s-(m*60)}s'


def format_bytes(b: int, per_second: bool = False) -> str:
    time: str = f'ps' if per_second else ''
    if b < 1024:
        return f'{r(b)}B{time}'
    k: float | int = b / 1024
    if k < 1024:
        return f'{r(k)}KB{time}'
    m: float | int = k / 1024
    if m < 1024:
        return f'{r(m)}MB{time}'
    g: float | int = m / 1024
    return f'{r(g)}GB{time}'


def r(n: float, n_digits: int = 2) -> float | int:
    o: float = round(n, n_digits)
    return int(o) if o.is_integer() else o


if __name__ == '__main__':
    print(format_bytes(654342, per_second=True))
