"""
this file gathers functions for stretching frequencies of mixed p-g modes
"""

import numpy as _np
from .generate_spectra import generate_asymp_p
from ..Freq import Freq, ModeSet

__all__=['zeta','tau_mod_Pi1']

def tau_mod_Pi1(mode, Pi1, par_p, q, nu_unit='muHz', P_unit='s'): #Ong & Gehan 2021
    """!tau Ong & Gehan"""

    if not isinstance(mode, ModeSet): mode=ModeSet(mode, nu_unit)

    theta,_=theta_Dnu(mode, par_p)

    if isinstance(Pi1, Freq): Pi1=Pi1.getv(P_unit)

    r = mode.getv(P_unit) + Pi1/_np.pi * _np.arctan(q/_np.tan(theta))
    r = r%Pi1

    er = mode.gete(P_unit)/zeta(mode, Pi1, par_p, q, nu_unit,P_unit)

    return r, er

def zeta(mode, Pi1, par_p, q, nu_unit='muHz', P_unit='s'):

    if not isinstance(mode, ModeSet): mode=ModeSet(mode, nu_unit)
    nu=mode.getv(nu_unit)

    theta,Dnu=theta_Dnu(mode,par_p, nu_unit)

    if not isinstance(Pi1, Freq): Pi1=Freq(Pi1, P_unit)
    Pi1_i=Pi1.getv(nu_unit)

    tmp=_np.sin(theta)**2 + (_np.cos(theta)*q)**2

    tmp = 1. + q * nu**2 / (Pi1_i*Dnu*tmp)

    return 1./tmp

def theta_Dnu(mode, par_p, nu_unit='muHz'):

    if not isinstance(mode, ModeSet): mode=ModeSet(mode, nu_unit)
    nu=mode.getv(nu_unit)

    mode1=generate_asymp_p(par_p, l=1, nu=(min(nu),max(nu)), unit=nu_unit)
    nup=mode1.getv(nu_unit)

    i0=_np.searchsorted(nup, nu)-1
    nup0=nup[i0]
    Dnu =nup[i0+1]-nup[i0]
    theta=_np.pi*(nu-nup0)/Dnu

    return theta, Dnu
