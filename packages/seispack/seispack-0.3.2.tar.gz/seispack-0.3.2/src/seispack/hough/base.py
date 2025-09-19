from .core import *
from .util import resolution_estimate, valid_k
import numpy as np

__all__ = ["lambda_val", "hough_profile"]


def lambda_val(s, m, *, k=None, l=None, nt=None, missing=-1e99):

    k=valid_k(m,k,l)

    odd=k%2

    if(abs(s)<=1. and k<0): return missing
    if(m==0 and k==0): return 0.

    if(nt is None): nt=resolution_estimate(s,m,k)

    S=Spectrum(MatWi(m,odd,s,nt=nt),kmin=k,kmax=k)
    if(S.lamb.ndim!=1):
        print(S.lamb, S.lamb.size, S.lamb.ndim, m,odd,s)
        raise KeyError
    match S.lamb.size:
        case 0:return missing
        case 1:return S.lamb[0]
        case _:raise TypeError('should not occur S.lamb must be an empty array or a scalar')


def hough_profile(s, m, *, k=None, l=None, nt=256, ntmax=None, missing=-1e99):

    k=valid_k(m,k,l)

    odd=k%2

    if(abs(s)<=1. and k<0): return missing
    if(m==0 and k==0): return 0.

    if(ntmax is None): ntmax=resolution_estimate(s,m,k)

    S=Spectrum(MatWi(m,odd,s,nt=ntmax),kmin=k,kmax=k)
    if(S.lamb.ndim!=1):
        print(S.lamb, S.lamb.size, S.lamb.ndim, m,odd,s)
        raise KeyError
    match S.lamb.size:
        case 0:
            x,w = np.polynomial.legendre.leggauss(nt)
            y=x*0.+missing
            return x,y,y,y,w
        case 1:return hough(S,nt)
        case _:raise TypeError('should not occur S.lamb must be an empty array or a scalar')
