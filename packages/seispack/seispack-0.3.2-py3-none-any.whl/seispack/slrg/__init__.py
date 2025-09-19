"""!
It provides tools to analyze solar-like and red giants stars (slrg)

@author Jérôme Ballot
"""

from .plot_stretch import plot_stretch
plot_sed=plot_stretch
from .plot_echelle import plot_echelle
plot_ced=plot_echelle
from .plot_echelle_image import plot_echelle_image
from .eacf import eacf
from .psd import psd
from .Model import ModelAsympRG
from .generate_spectra import *
from .stretch import zeta, tau_mod_Pi1
from .bg_tools import normalise_to_noise