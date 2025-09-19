"""!
Package computing Hough functions and associated eigenvalues within asymptotic approximations from Townsend 2003, 2020 or Lignières+2024

@author Jérôme Ballot
"""

import numpy as _np
from scipy.special import hermite
from .util import valid_k

__all__ = [ 'lambda_a', 'lambda_a_arr', 'hough_a' ]

def lambda_a(s, m, *, k=None, l=None, approx='full'): #ok even if s<0

    k = valid_k(m,k,l)
    if(abs(s)==0):
        return -1.e99

    if((s*m)<=0): #prograde or zonal
        if(k==0): # kelvin
            return 2*s*m**3/(2*m*s+1)
        else: #g prograde
            p=k-1
    else: #retrograde
        p=abs(k+1)

    P=2*p+1
    if approx=='Townsend':
        if(k<-1):
            return ((m/P)*(1-m/s))**2
        else:
            return (P*s)**2

    a=m*(m-s)
    ks2=0.5*(P*s)**2
    sD=_np.sqrt(1+2*a/ks2)

    if(k<-1):
        return a+ks2*(1-sD)
    else:
        return a+ks2*(1+sD)

lambda_a_arr=_np.vectorize(lambda_a)


def hough_a(x, s, m, *, k=None, l=None, lam=None): #ok even if s<0

    k = valid_k(m,k,l)

    if((s*m)<=0): #prograde or zonal
        if(k==0): # kelvin
            mms=-m*s
            tau = x*_np.sqrt(mms)
            fac=1./(1.-2.*mms)
            Hr=_np.exp(-0.5*tau**2)
            Ht=-m**2*fac/_np.sqrt(mms)*tau*Hr
            Hp=-m*(1.+fac*tau**2)*Hr
            return Hr, Ht, Hp
        else: #g prograde
            p=k-1
    else: #retrograde
        p=abs(k+1)

    if p<0:
        print("prograde and negative k => p<0 ... stop")
        Hr = x*0
        Ht = x*0
        Hp = x*0
        return Hr, Ht, Hp

    if lam is None: lam=lambda_a(s,m,k=k)
    if lam<0:
        print("negative lambda ... stop")
        Hr = x*0
        Ht = x*0
        Hp = x*0
        return Hr, Ht, Hp

    L=_np.sqrt(lam)
    if(s<0): # hereafter s is assumed to be > 0
        s=-s
        m=-m
    sig=x*_np.sqrt(L*s)
    gauss=_np.exp(-0.5*sig**2)
    He=hermite(p)
    if p>0:
        Hem=hermite(p-1)
    else:
        Hem=0.
    Hep=hermite(p+1)

    Ht=He*gauss
    Hr=_np.sqrt(L*s)/(L**2-m**2)*(p*(m/L+1)*Hem(sig)+0.5*(m/L-1)*Hep(sig))*gauss
    if(m==0):
        Hp=-_np.sqrt(L*s)/(L**2)*(p*L*Hem+0.5*L*Hep)*gauss
    else:
        Hp=m*_np.sqrt(L*s)/(m**2-L**2)*(p*(L/m+1)*Hem(sig)+0.5*(L/m-1)*Hep(sig))*gauss

    return Hr, Ht, Hp
