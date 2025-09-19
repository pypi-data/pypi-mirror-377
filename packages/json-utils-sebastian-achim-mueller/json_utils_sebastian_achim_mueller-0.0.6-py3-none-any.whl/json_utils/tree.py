import glob
import os
import json_numpy
from .utils import read as read_single_json_file
from .utils import write as write_single_json_file


def read(path):
    """
    Walks down a directory and reads every json-file into an object.

    Parameter
    ---------
    path : str
        Path of the directory to be read.

    Returns
    -------
    tree : dict
        One combined object with the top-level keys beeing the dirnames
        and basenames of the json-files.
    """
    out, _ = read_with_dirtree(path=path)
    return out


def read_with_dirtree(path):
    """
    Parameters
    ----------
    path : str
        Base of the directory and json-file tree.

    Returns
    -------
    tree : dict
        The actual payload read from the json-files.
    dirtree : dict
        Meant to preserve the directory structure.
        Same keys (dirnames) as in tree but without the payload.

    See also tree.write(path).
    """
    out = {}
    dirtree = {}
    _paths = glob.glob(os.path.join(path, "*"))
    for _path in _paths:
        file_path, file_extension = os.path.splitext(_path)
        file_basename = os.path.basename(file_path)
        if str.lower(file_extension) == ".json":
            out[file_basename] = read_single_json_file(_path)
        if os.path.isdir(_path):
            out[file_basename], dirtree[file_basename] = read_with_dirtree(
                path=_path
            )
    return out, dirtree


def write(path, tree, dirtree, indent=4):
    """
    Write a tree into directories and json-files.

    Parameters
    ----------
    path : str
        The base directory to write the tree to.
    tree : dict
        The payload to be written to path.
    dirtree : dict
        Meant to preserve the directory structure.
        Same as tree but without the actual payload. A key in tree which is
        also in dirtree will be written as a directory. Else, when a key in
        tree is not in dirtree, the payload in tree[key] will be written to a
        json-file.
    indent : int
        Number of spaces used to indent json-files.
    """
    os.makedirs(path, exist_ok=True)
    for key in tree:
        if key in dirtree:
            write(
                path=os.path.join(path, key),
                tree=tree[key],
                dirtree=dirtree[key],
            )
        else:
            write_single_json_file(
                path=os.path.join(path, key + ".json"),
                out=tree[key],
                indent=indent,
            )
