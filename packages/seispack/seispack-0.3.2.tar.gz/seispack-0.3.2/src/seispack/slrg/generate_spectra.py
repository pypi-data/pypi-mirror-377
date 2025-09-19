import numpy as np
from math import floor
from math import ceil
from ..Freq import *


"""!generate asymptotic spectrum of for read giants"""

__all__ = ['generate_asymp_p' ]


def generate_asymp_p(p_param, rot_p=0., *, l=0, m=0, n=(-5,5), nu=(None,None), unit='muHz'):
    """!generates asymptotic p mode spectrum"""

    l_all=np.array(l).flatten()
    m_all=np.array(m).flatten()

    mode=ModeSet()
    numax=p_param[0]
    Dnu=p_param[1]
    eps_p=p_param[2]
    a_2=p_param[3]
    if isinstance(numax, Freq): numax=numax.getv(unit)
    if isinstance(Dnu, Freq): Dnu=Dnu.getv(unit)
    if isinstance(rot_p, Freq): rot_p=rot_p.getv(unit)
    nmax=numax/Dnu
    n1=round(nmax)+n[1]

    if nu[0] is None:
        n0=max((round(nmax)+n[0]),1)
    else:
        if isinstance(nu[0], Freq):
            nu0=nu[0].getv(unit)
        else:
            nu0=nu[0]
        n0=np.floor(nu0/Dnu-eps_p)
        n0=max(int(n0)-1,1)

    if nu[1] is None:
        n1=round(nmax)+n[1]
    else:
        if isinstance(nu[1], Freq):
            nu1=nu[1].getv(unit)
        else:
            nu1=nu[1]
        n1=np.ceil(nu1/Dnu-eps_p)
        n1=int(n1)+1

    for l in l_all:
        n0l=max(n0-l//2,0)
        n1l=n1-l//2
        n=np.arange(n0l,n1l+1)
        n_real=n+0.5*l+eps_p
        if len(p_param)<3+l:
            continue #skip missing d0n
        if l>0:
            d0n = p_param[3+l]
            if isinstance(d0n, Freq): d0n=d0n.getv(unit)
        else:
            d0n = 0.
        #nu0 = Dnu*(n_real+a_2*(n_real-nmax)**2-d0n*nmax/n_real)
        nu0 = Dnu*(n_real+0.5*a_2*(n_real-nmax)**2)-d0n
        for m in np.arange(-l,l+1):
            if m in m_all:
                nu=nu0-m*rot_p
                mode.append(ModeSet(nu, unit, l=l, m=m, n=n))

    return mode
