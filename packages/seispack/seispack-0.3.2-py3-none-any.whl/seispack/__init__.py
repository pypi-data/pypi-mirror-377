"""!
package for asteroseismic data analysis

@author Jérôme Ballot
"""
import importlib.metadata as _metadata

try:
    from ._version import __version__
except ImportError:
    try:
        __version__ = _metadata.version(__package__)
    except _metadata.PackageNotFoundError:
        __version__ = "unknown version"


from .basic import *
from .Freq import *
from .PSD import PSD, LightCurve
from .data import *
from .tar import *
from .slrg import *
