import numpy as _np
from matplotlib.ticker import FixedLocator
from math import ceil as intceil
from numbers import Integral

def scaleLS(l):
    return _np.log10(1.+abs(l))*_np.sign(l)

def scaleLS_inv(s):
    return (10.**abs(s)-1)*_np.sign(s)

def set_scaleLS(ax):
    scalel=_np.array([0]+list(10**_np.arange(0,10))+list(-10**_np.arange(0,10)))
    ax.set_yscale('function', functions=(scaleLS, scaleLS_inv))
    ax.yaxis.set_major_locator(FixedLocator(scalel))

def valid_k(m,k,l):
    if not isinstance(m, Integral):
        raise TypeError(f'm must be an Integer, not {type(m)}')
    if k is None:
        if l is None:
            raise TypeError('k and l cannot be both None')
        elif isinstance(l, Integral):
            k=l-abs(m)
        else:
            raise TypeError(f'l must be an Integer, not {type(l)}')
    else:
        if not isinstance(k, Integral):
            raise TypeError(f'k must be an Integer, not {type(k)}')
        if l is not None:
            if isinstance(l, Integral):
                if(k != l-abs(m)):
                    raise ValueError(f'm,k,l are not compatible ({m},{k},{l})')
            else:
                raise TypeError(f'l must be an Integer, not {type(l)}')
    return k

def find_lmax(TabSp):
    lmax=_np.size(TabSp,axis=0)
    l0=lmax//2
    eps=2*_np.finfo(float).eps
    while(lmax>l0+2):
        if (TabSp.ndim==1):
            test=_np.any(abs(TabSp[l0:])>eps)
        else:
            test=_np.any(abs(TabSp[l0:,:])>eps)
        if(test):
            l0=(lmax+l0)//2
        else:
            lmax=l0
            l0=l0//2
    return lmax

def resolution_estimate(s,m,k):
    if m*s>0:
        kp=k+2
    else:
        kp=k
    if(kp>=0):
        nt=intceil(1.2*(3+1.33*kp)*abs(s)) #1.2 factor above the empirical limit determined for g modes
        nt=max(3+2*max(kp,2),nt) # provide a minimal resolution at low s
        if(k<0): nt=max(nt,2*abs(m)+2*abs(k))
    else: #needed to be rewrite if < lambda are needed
        nt=64
    return nt
