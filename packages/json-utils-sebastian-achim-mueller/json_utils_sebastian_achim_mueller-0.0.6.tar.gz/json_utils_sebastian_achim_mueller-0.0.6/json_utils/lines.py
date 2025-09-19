import json_numpy
import builtins
import gzip


def open(path, mode="r"):
    """
    Read or write json lines.

    Parameters
    ----------
    path : str
        Path to file.
    mode : str
        Either of ['r', 'r|gz', 'w', 'w|gz']. The 't' for text can be added but
        is ignored.

    Returns
    -------
    reader/writer : Reader/Writer
        Depending on mode.
    """
    assert not "b" in mode, "Expected text-mode 't' and not binary 'b'."
    if "r" in mode:
        if "|gz" in mode:
            return Reader(file=gzip.open(path, "rt"))
        else:
            return Reader(file=builtins.open(path, "rt"))
    elif "w" in mode:
        if "|gz" in mode:
            return Writer(file=gzip.open(path, "wt"))
        else:
            return Writer(file=builtins.open(path, "wt"))
    else:
        raise ValueError("Expected mode to contain either 'w' or 'r'.")


def write(path, obj_list, mode="w"):
    with open(path=path, mode=mode) as jlwr:
        for obj in obj_list:
            jlwr.write(obj)


def read(path, mode="r"):
    obj_list = []
    with open(path=path, mode=mode) as jlre:
        for obj in jlre:
            obj_list.append(obj)
    return obj_list


class Reader:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        line = self.file.__next__().strip()
        return json_numpy.loads(line)

    def __repr__(self):
        out = "{}(".format(self.__class__.__name__)
        out += ")\n"
        return out


class Writer:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def write(self, obj):
        line = json_numpy.dumps(obj, indent=None)
        self.file.write(line)
        self.file.write("\n")

    def __repr__(self):
        out = "{}(".format(self.__class__.__name__)
        out += ")\n"
        return out
