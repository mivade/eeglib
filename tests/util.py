import os.path as osp


def get_abspath(relpath):
    """Return absolute path to a file/directory given a relative path."""
    return osp.abspath(osp.join(osp.dirname(__file__), relpath))
