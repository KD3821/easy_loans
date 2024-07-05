import importlib

from .common import *

# try to import environment configuration module
mdl = importlib.import_module(f"settings.{ENV}")

if "__all__" in mdl.__dict__:
    names = mdl.__dict__["__all__"]
else:
    # otherwise we import all names that don't begin with _
    names = [x for x in mdl.__dict__ if not x.startswith("_")]

globals().update({k: getattr(mdl, k) for k in names})
