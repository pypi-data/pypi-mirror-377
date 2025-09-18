from ..Freq import *
from ..hough import lambda_val
from ..hough import load_lambda_tables
from ..hough import valid_k
import numpy as np
from scipy.optimize import root_scalar
from scipy.interpolate import make_interp_spline

__all__ = [ 'generate_aTAR' ]

def func_root(s, c, ne, m, k):
    """!computes s*sqrt(lambda(s))"""
    res=s*np.sqrt(max(0.,lambda_val(s,m,k=k)))
    res*=c
    res-=ne
    return res


def generate_aTAR(Pi0: Freq|float, rot: Freq|float, eps: float, n, m: int, *, k=None, l=None, lambda_table=None, use_table=True):
    """!compute a mode or series of modes (m,l) or (m,k) following the asymptotic TAR
    @param Pi0 Freq|float: Buoyancy radius of the star. If float, assumed to be in second
    @param rot Freq|float: rotation of the star. It float, assumed to be the period in days
    @param eps float: phase shift of the asymptotic development
    @param n int|array|tuple(nmin:int,nmax:int): radial order(s). If tuple array from nmin to max is generated
    @param m int: azimuthal order
    @param k int: k index of the series. must be provided except if l is.
    @param l int: degree of the series. Ignored if k is provided
    @param lambda_table tuple(s:array,lambda:array): tables containing lambda_{m,k} for each spin parameter s.
            If not provided, it loads the default tables. If tables are missing, lambda is computed on the fly

    @return Mode|ModeSet: contains the set of computed modes.
            The result is a Mode only when n is an int.
    """
    if not isinstance(Pi0, Freq):
        #assumed Pi0 in second
        Pi0=Freq(Pi0,'s')
    if not isinstance(rot, Freq):
        #assumed rot in days
        rot=Freq(rot,'d')

    two_rotHz=2*rot.getv('Hz')
    c=two_rotHz*Pi0.getv('s')
    c=1./c

    if isinstance(n, tuple):
        if(len(n) !=2):
            raise ValueError('when n is a tuple, two elements are expected (nmin, nmax)')
        else:
            n=np.arange(n[0],n[1]+1)
    else:
        n=np.array(n)

    if n.size<1: raise ValueError('when n is empty')
    isscalar=(n.ndim==0)
    n=n.flatten()

    k=valid_k(m,k,l)

    modes=ModeSet([])
    if k<0:
        if m<1: return modes #no modes
        smin=(m-k)*(m-k-1)/m #Rossby modes
    else:
        if k==0 and m==0: return modes #no modes
        smin=0.
    smax=100.

    if use_table and lambda_table is None:
        lambda_table = load_lambda_tables(m,k=k, l=l)
    if(isinstance(lambda_table, tuple)):
        s,lamb = lambda_table
        indp=lamb>=0.
        x=c*s[indp]*np.sqrt(lamb[indp])
        bspl = make_interp_spline(x, s[indp], k=3)
        if(max(x)<max(n+eps)):
            print("n is too large for the spin parameter range of the table")
            return modes
        s_sol = bspl(n+eps)
        Ps=s_sol/two_rotHz
        modes=ModeSet(Ps,'s',m=m,k=k,n=n,rot=rot,corot=True)
        if isscalar: return modes[0]
    else:
        for nn in n:
            sol=root_scalar(func_root, args=(c, nn+eps, m, k), bracket=[smin, smax], method='brentq')
            s_sol=sol.root
            Ps=s_sol/two_rotHz
            mode=Mode(Ps,'s',m=m,k=k,n=nn,rot=rot,corot=True)
            if isscalar: return mode
            modes.append(mode)

    return modes

