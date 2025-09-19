"""Tiny importer: resolves a dotted path string to a Python object."""

import importlib


def import_obj(dotted: str):
    module, attr = dotted.rsplit(".", 1)
    mod = importlib.import_module(module)
    return getattr(mod, attr)
