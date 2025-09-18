"""
Package computing Hough functions and associated eigenvalues following
Unno, Wasaburo ; Osaki, Yoji ; Ando, Hiroyasu ; Saio, H. ; Shibahashi, H.
Nonradial oscillations of stars, Tokyo: University of Tokyo Press, 1989, 2nd ed.

It also include asymptotic computations from Townsend 2003, 2020 or Lignières+2024

@author Jérôme Ballot
"""
__all__= []
from .base import *
__all__+=base.__all__
from .core import *
__all__+=core.__all__
from .asymptotic import *
__all__+=asymptotic.__all__
from .util import *
from .tables import *
__all__+=tables.__all__
