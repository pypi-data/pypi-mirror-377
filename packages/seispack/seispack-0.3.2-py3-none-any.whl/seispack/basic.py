"""
Gather simple routines that manipulates numpy array in an "idl-like" way

@author Jérôme Ballot
"""

import numpy as np

__all__ =[ 'smooth', 'rebin', 'a_correlate']

def smooth(tab:np.ndarray, n:int):
    """!
    smooth an array with a convolution with a boxcar.
    Beyond boundaries, the array is extended with symmetrical arrays.
    @param  tab: Array to smooth
    @param  n: size of the boxcar (odd values are recommended)
    """
    return np.convolve(
        np.concatenate( (tab[n//2-1::-1], tab, tab[:-n//2:-1]) ),
        np.ones(n)/n,
        mode='valid')

def rebin(vec, n, *, ifirst=0, nskip=0):
    """
    rebin the 1D array vec with a factor of n
    the ifirst first points are ignored (ifirst is the index of the first point taken into account)
    when averaged, the nksip last points of each set of n points are ignored
    The function rebins k points every n points, where k = n - nskip
    """
    if(nskip>=n):
        print('nskip must be smaller than n')
        return vec
    ninit=vec.size
    nfin=(ninit-ifirst+nskip)//n
    ilast=nfin*n+ifirst
    if  ilast > ninit:
        tmp=np.pad(vec,(0,nskip))
    else:
        tmp=vec

    return tmp[ifirst:ilast].reshape((nfin,n))[:,:n-nskip].mean(1)

def a_correlate(x, lag):
    """! compute the auto-correlation of an array as a function of the lag
    @param x: 1-D array to process
    @param lag: list or 1-D array of integers specifying the signed distances
                between indexed elements of x. It must verify |lag| < x.size
    """
    c=np.zeros(len(lag))
    y=x-x.mean()
    for i,l in enumerate(lag):
        c[i]= (y[l:]*y[:x.size-l]).sum()
    return c / x.var() / x.size
