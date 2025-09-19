"""
Compute Hough functions and associated eigenvalues following
Unno, Wasaburo ; Osaki, Yoji ; Ando, Hiroyasu ; Saio, H. ; Shibahashi, H.
Nonradial oscillations of stars, Tokyo: University of Tokyo Press, 1989, 2nd ed.

@author Jérôme Ballot
"""

import numpy as np
from scipy.linalg import eigh_tridiagonal as tegv
from scipy.special import sph_harm_y
from math import floor as intfloor

__all__ = ["MatWi","Spectrum","hough"]

class MatWi:
    """!Representation of a matrix W^-1, a truncation of the inverse of the matrix W
    defined in Unno et al. obtained within the Traditional Approximation of Rotation
    This matrix W^-1 is symmetric and tridiagonal

    @param m: int is the azimuthal order
    @param odd = 0 or 1 whether modes are even/odd relative to the equator
    @param eta is the spin parameter
    @param nt (default: 200) resolution in latitude, i.e. matrix size, i.e.
    number of Legendre associated polynomials to be used.

    Convention used here: Prograde mode have m*eta < 0

    """
    def __init__(self, m: int, odd: int, eta: float, *, nt: int=200):
        self.diag, self.offdiag, self.l, self.ind_kp0, self.eps, self.singular = invW(m,odd,eta,nt=nt)
        self.m = m
        self.odd = odd
        self.eta = eta
        self.nt = nt

    def __repr__(self):
        odd_str='even' if self.odd==0 else 'odd'
        return f'MatWi(m={self.m:0d} {odd_str}, eta={self.eta:.6g}, nt={self.nt:0d})'

class Spectrum:
    """Representation of the spectrum of W for k between kmin and kmax"""
    def __init__(self, Wi, *args, **kargs):
        self.lamb, self.HoughSp, self.k = spectrum(Wi, *args, **kargs)
        self.l = Wi.l
        self.m = Wi.m
        self.eta = Wi.eta
        self.odd = Wi.odd
        self.nt = Wi.nt
        self.nk =self.k.size

    def __repr__(self):
        odd_str='even' if self.odd==0 else 'odd'
        return f'Spectrum(m={self.m:0d} {odd_str}, eta={self.eta:.6g}, k=[{self.k.min()},{self.k.max()}], nt={self.nt:0d})'


#----------------------------------------------------------------------
def CoefJ(l,m):
    """coefficient J_l^m as defined in Unno+(1990)/Lee&Saoi(1987)"""
    if l <= abs(m):
        return 0.
    else:
        return np.sqrt((l-m)*(l+m)/(4*l**2-1))

#----------------------------------------------------------------------
VCoefJ = np.vectorize(CoefJ)

#----------------------------------------------------------------------
def invW(m: int, odd: int, eta: float, *, nt: int=200):
    """!
    Compute a truncation of the inverse of the matrix W defined in Unno et al.
    obtained within the Traditional Approximation of Rotation
    This matrix W^-1 is symmetric and tridiagonal

    @param m: int is the azimuthal order
    @param odd = 0 or 1 whether modes are even/odd relative to the equator
    @param eta is the spin parameter
    @param nt (default: 200) resolution in latitude, i.e. matrix size, i.e.
    number of Legendre associated polynomials to be used.

    Convention used here: Prograde mode have m*eta < 0

    @return  d, e, l, ind_kp0, eps, singular
    d: array(nt) diagonal term of W^-1
    e: array(nt-1) upper (lower) diagonal
    l: array containing the degree of Legendre associated polynomials to be used
        l=|m|+odd+2*j for j=0,nt
        except for ven m=0 modes: l=2+2*j for j=0,nt (since l>0)
    ind_kp0: int index of k=0 among the positive eigenvalues of W (when Rossby modes appear, this index increases)
    singular: bool indicates W is singular
    eps: float if small, W is close to be singular

    """

    if(m%1 != 0):
        raise ValueError("m must be an integer; m={}".format(m))
    if(odd != 0 and odd !=1):
        raise ValueError("Only odd = 0 or 1 are valid; odd={}".format(odd))

    am=abs(m)
    meta=m*eta
    singular=False

    l=am+2*np.arange(nt)+odd
    kp0 = odd # value of the first value of positive k (as defined in Lee&Saoi 1997)
    if(am==0 and odd==0):
        l=l+2 #to remove l=0
        kp0 = 2 # for m=0, k=0 is not considered since lamdba=0 in this case

    if(meta>0. and abs(eta)>1.):
        # new r-modes can appear:
        # 1) possible singular matrix
        # 2) k=0 is not necessarily the lowest positive eigenvalue

        test = (1+2*(odd-am)+np.sqrt(4*meta+1))/4 #root of l(l-1)=meta with l=|m|+2k-odd >> identify the appearance of r-modes
        singular=(test>0.9 and test.is_integer()) # if test=k is an integer >=1, a r-mode with lambda=0 appears > the matrix is symmetric

        #singular=(test>0.9 and abs(test-round(test))<1e-7) #alternative to identify cases where test is almost integer

        ind_kp0=max(0,intfloor(test)) #index of first positive k (as defined in Lee&Saoi 1997)
        tmp=l[0]+2*round(test)
        eps=meta-tmp*(tmp-1) # if eps is small, the matrix may be close to be singular
    else: #no Rossby modes, thus g(i)-modes (k>=0) start at first index
        test=0.
        singular=False
        ind_kp0=0
        eps=1.


    if singular: old_setup=np.seterr(divide='ignore') #suppress warning due to division by zero

    lmmei=1./(meta-(l+1)*(l+2))
    llp1i=1./(l*(l+1))
    e=VCoefJ(l+1,m)*VCoefJ(l+2,m)*lmmei*eta**2 #upper (=lower) diagonal of W^-1
    e=e[:-1]

    d=np.zeros(nt) #diagonal of W^-1

    ind=(l!=1) & (l!=am) # the next term is zero for l=|m| and for l=1 (but will generate a 0/0 situation)
    ll=l[ind]
    llm1i=1/(ll*(ll-1))
    d[ind] = (eta*VCoefJ(ll,m))**2*(ll**2-1)/(ll**2*(meta*llm1i-1.))

    d = d + (eta*VCoefJ(l+1,m))**2*l*(l+2)**2/(l+1)*lmmei

    d = d + 1. - meta*llp1i
    d = d * llp1i

    if singular: np.seterr(**old_setup)

    return d, e, l, ind_kp0, eps, singular

#----------------------------------------------------------------------
def spectrum(W, kmin=-10, kmax=10, *, epslim=1e-4, deta=1.e-3, verbose=False):
    """
    compute the eigenvalues and eigenvectors of W only for k in [kmin, kmax]
    @param W: MatWi the representation of the equations to be solved.
    """

    if(not isinstance(W, MatWi)):
        raise ValueError("W must be an instance of MatWi;  type(W)={}".format(type(W)))

    #epslim=1e-4 #if W.eps < epslim, we consider that the eigenvalue computation may be degraded
    if W.singular or abs(W.eps)<epslim:
        if verbose: print('singular or close to singular => interpolate')
        #deta=1.e-3 # quadratic interpolation around the singular is performed from points with eta_k = eta_0+[-2,-1,1,2]*eps
        Wp =MatWi(W.m,W.odd,W.eta+deta,nt=W.nt)
        vp, vecp, kp = spectrum(Wp,kmin=kmin,kmax=kmax)
        Wm =MatWi(W.m,W.odd,W.eta-deta,nt=W.nt)
        vm, vecm, km = spectrum(Wm,kmin=kmin,kmax=kmax)
        k=np.intersect1d(kp,km,assume_unique=True)
        Wpp=MatWi(W.m,W.odd,W.eta+2*deta,nt=W.nt)
        vpp, vecpp, kpp = spectrum(Wpp,kmin=kmin,kmax=kmax)
        k=np.intersect1d(k,kpp,assume_unique=True)
        Wmm=MatWi(W.m,W.odd,W.eta-2*deta,nt=W.nt)
        vmm, vecmm, kmm = spectrum(Wmm,kmin=kmin,kmax=kmax)
        k=np.intersect1d(k,kmm,assume_unique=True)
        nk=len(k)
        v = np.zeros(nk)
        vec= np.zeros((W.nt,nk))
        for i in range(nk):
            v[i]=(4*vp[kp==k[i]]+4*vm[km==k[i]]-vpp[kpp==k[i]]-vmm[kmm==k[i]])/6
            iref=np.argmax(vecp[:,kp==k[i]])
            sigref=np.sign(vecp[iref,kp==k[i]])
            sigm=np.sign(vecm[iref,km==k[i]])*sigref
            sigpp=np.sign(vecpp[iref,kpp==k[i]])*sigref
            sigmm=np.sign(vecmm[iref,kmm==k[i]])*sigref
            vec[:,i]=((4*vecp[:,kp==k[i]]+4*sigm*vecm[:,km==k[i]]-sigpp*vecpp[:,kpp==k[i]]-sigmm*vecmm[:,kmm==k[i]])/6).squeeze()
            vec[:,i]=vec[:,i]/np.sqrt(np.sum(vec[:,i]**2)) # renormalise

        indp=np.argwhere(v>=0.)
        if(indp.size != 0): #we shift the indexes such that v[0] is the small positive eigenvalues
            v=np.roll(v,-indp[0])
            k=np.roll(k,-indp[0])
            vec=np.roll(vec,-indp[0],axis=1)
        return v,vec,k
    #end if singular (or quasi-singular matrix)


    vp,vec= tegv(W.diag,W.offdiag) #sorted min to max
    vp = 1./np.flip(vp) # lambda
    vec= np.flip(vec,axis=1)
    k = np.zeros(W.nt,dtype=int)
    if(W.m==0 and W.odd==0):
        kp0 = 2     # first positive k in the list is 2 when m==0
    else:
        kp0 = W.odd # first positive k in the list

    kn0 = W.odd - 2 # first negative k in the list -1 or -2

    n_pos = np.count_nonzero(vp>0.) #how many positive eigenvalue

    if(n_pos==W.nt):
        #verif:
        if(W.ind_kp0 != 0):
            print("something goes wrong: all eigenvalues are positive, W.ind_kp0 must be 0")
        k = kp0+2*np.arange(n_pos)

    else:
        if(abs(W.eta)<1.):
            print("something goes wrong: for |eta|<1, all eigenvalue must be positive")

        k = np.zeros(W.nt,dtype=int)

        nkp = n_pos - W.ind_kp0
        nkn = W.nt - nkp

        k[W.ind_kp0:W.ind_kp0+nkp] = kp0 + 2*np.arange(nkp)

        ind_kn = W.ind_kp0 - 1 - np.arange(nkn)

        kn0 = W.odd - 2 # first negative k in the list is -1 or -2
        k[ind_kn]= kn0 - 2 * np.arange(nkn)

    indok=np.argwhere((k>=kmin) & (k<=kmax)).squeeze(1)

    k=k[indok]
    vp=vp[indok]
    vec=vec[:,indok]

    return vp,vec,k

#----------------------------------------------------------------------
def hough(Sp,nth=1024):
    """!
    compute the Hough functions from their spectral decomposition (over Legendre associated polynomials)
    @param Sp: Spectrum
    @param nth (default:1024) latitudinal resolution

    @result x,Hr,Ht,Hp,w
        x: array containing the grid cos(theta). It follows a Gauss-Legendre quadrature
        Hr: (radial) Hough function
        Ht: latitudinal Hough function
        Hp: azimutal Hough function
        w: associated weights of the Gauss-Legendre quadrature
    """

    x,w = np.polynomial.legendre.leggauss(nth)
    s=np.sqrt(1.-x*x)
    theta = np.arccos(x)
    eps=np.finfo(float).eps

    nk=Sp.k.size

    Hr = np.zeros((nth,nk))
    Ht = np.zeros((nth,nk))
    Hp = np.zeros((nth,nk))
    il=0
    m=Sp.m
    am=abs(m) #verifier dans la suite...
    #lmax=find_lmax(Sp.HoughSp)
    lmax=len(Sp.l)
    for il in range(lmax):
        if(np.any(abs(Sp.HoughSp[il,:])>eps)):
            l=Sp.l[il]
            Plm=sph_harm_y(l,m,theta,0.).real
            if(l>am):
                Pl1m=sph_harm_y(l-1,m,theta,0.).real
                fac=np.sqrt((l-m)*(l+m)*(2*l+1)/(2*l-1))
            else:
                Pl1m=np.zeros(nth)
                fac=0.
            for ik in range(nk):
                if(abs(Sp.HoughSp[il,ik])>eps):
                    Hr[:,ik] += Sp.HoughSp[il,ik]*Plm
                    Ht[:,ik] += Sp.HoughSp[il,ik]*((l+m*Sp.eta)*x*Plm-fac*Pl1m)
                    Hp[:,ik] += Sp.HoughSp[il,ik]*((fac*Sp.eta)*x*Pl1m-((l*Sp.eta)*x**2+m)*Plm)


    for ik in range(nk):
        Ht[:,ik]=Ht[:,ik]/(1-(x*Sp.eta)**2)
        #Ht[:,ik]=Ht[:,ik]/s[:] #Townsend or Lignieres...
        Hp[:,ik]=Hp[:,ik]/(1-(x*Sp.eta)**2)
        #Hp[:,ik]=Hp[:,ik]/s[:]
        # Ht[1:-1,ik]=Ht[1:-1,ik]/s[1:-1]
        # Ht[0,ik]=extrap(x[0],x[1:],Ht[1:,ik])
        # Ht[-1,ik]=extrap(x[-1],x[:-1],Ht[:-1,ik],left=False)
    return x,Hr,Ht,Hp,w
