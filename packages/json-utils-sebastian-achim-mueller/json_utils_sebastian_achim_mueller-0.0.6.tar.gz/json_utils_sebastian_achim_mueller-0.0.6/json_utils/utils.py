import json_numpy


def write(path, out, indent=4):
    """
    Write `out` to `path`.
    """
    with open(path, "wt") as f:
        f.write(json_numpy.dumps(out, indent=indent))


def read(path):
    """
    Read dict from `path`.
    """
    with open(path, "rt") as f:
        out = json_numpy.loads(f.read())
    return out
