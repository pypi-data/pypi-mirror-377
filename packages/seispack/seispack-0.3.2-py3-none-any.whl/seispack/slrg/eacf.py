import numpy as np
from ..PSD import PSD
from ..Freq import Freq
from .bg_tools import normalise_to_noise
from ..basic import rebin
from .scaling_law import Dnu_from_numax, lawc, lawe
__all__ = [ 'eacf' ]

def eacf(spectrum, /, *, nurange=None, fac=1.15, over=10, nDnu=5, rebin_factor=3, verbose=True):
    """!
    look for the large separation of a spectrum by computing it envelope autocorrelation function.
    In the current version, no significance is returned.
    @param spectrum: an instance of the PSD class,
                or a tupple of two array containing the frequencies (in µHz)
                and the power spectrum (or the spectral density)
                frequencies are assumed to be evenly sampled

    optional inputs
    @param nurange: 2-elements list containing the interval to scan for numax, express in µHz
                    The interval goes from nurange[0] to nu.max + nurange[1]
    @param fac: from one step to the next, tested numax is multiplied by fac (default 1.2)
    @param over: oversampling used to compute the FFT (default: 10)
    @param nDu: controls the width of the envelop on which the ACF is performed.
                it is provided in unit of large separation (default: 5)
    @param rebin_factor: rebin the spectrum to speed-up the computation (default: 3)
    @param verbose bool: print message if possible problems occur (default: True)
    @result Dnu_eacf, numax_eacf, max_correl, status: large separation and numax found by the method,
            correlation level and status (==0 if ok)
    No error estimate are performed.
    After:
     - I. W. Roxburgh & S. V. Vorontsov (2006), MNRAS 369, 1491
     - B. Mosser & T. Appourchaux (2009), A&A 508, 877
    """

    if not isinstance(spectrum, PSD):
        spectrum=PSD(*spectrum)

    spectrum.to_xunit('µHz')

    if spectrum.yunit!='S/N':
        if verbose: print('compute S/N spectrum')
        spectrum=normalise_to_noise(spectrum)

    nu=spectrum.x
    sp=spectrum.y

    if rebin_factor>1:
        nu=rebin(nu,rebin_factor)
        sp=rebin(sp,rebin_factor)

    numax_max=8000. #maximal value of numax.

    if nurange is None:
        if nu.max()>1000: #short cadence data
            nurange=[100.,-500.]
        else: # long cadence data
            nurange=[10.,-50.]
    if nurange[1]>0.:
        raise ValueError(f'nurange[1] must be negative {nurange[1]}')
    numax=nurange[0]
    nuend=min(nu.max()+nurange[1],numax_max)
    nubin=nu[1]-nu[0]
    x=[]
    y=[]
    nuc=[]

    q=1.5*fac**(0.5*lawe)

    while (numax<nuend):
        Dnu=Dnu_from_numax(numax)
        nuindex=(nu>numax-nDnu*Dnu)&(nu<numax+nDnu*Dnu)
        sp1=sp[nuindex]
        sp1=sp1
        npt=sp1.size
        sp1=sp1*np.hanning(npt)
        sp1=np.pad(sp1,(0,(over-1)*npt))
        imax=(over*npt)//2
        acf=np.abs(np.fft.ifft(sp1, n=imax)**2)
        acf=acf/acf[0]
        tacf=np.fft.fftfreq(imax,d=nubin)
        i0=max(4*over,int(2/(tacf[1]*Dnu)/q))
        i1=min(imax,int(2/(tacf[1]*Dnu)*q))
        acf_red=acf[i0:i1]
        y.append(acf_red.max())
        x.append(tacf[i0+np.argmax(acf_red)])
        nuc.append(numax)
        numax = numax*fac

    x=np.array(x)
    y=np.array(y)
    nuc=np.array(nuc)


    #i=np.argmax(y)
    isort=np.argsort(y)[::-1]
    jmax=0
    i=isort[jmax]

    correl=np.sqrt(y[i])
    Dnu_eacf=2./x[i] # Dnu=2/tau
    numax_eacf = nuc[i]

    status=-1
    if(i > 0 and i < y.size-1): #interpolate maximum
        if abs(x[i-1]/x[i]-1)<0.1 and abs(x[i+1]/x[i]-1)<0.1:
            Dp=np.log(y[i+1]/y[i])
            Dm=np.log(y[i-1]/y[i])
            correction=0.5*(1.+fac)*(Dp/fac**2+Dm)/(Dp/fac+Dm)
            status=0
        else:
            if verbose: print("warning: no 3 consecutive detections")
            correction=1.
            status=-1

    elif(i==y.size-1): #extrapolate maximum
        if abs(x[i-1]/x[i]-1)<0.1:
            status=-2
            correction=1.
        else:
            status=-1
            correction=1.
    else:
        status=-1
        correction=1.


    numax_eacf = numax_eacf*correction

    lnfac=lawe*np.log(numax_eacf)+np.log(lawc)-np.log(Dnu_eacf)

    roundfac = int(np.round(lnfac/np.log(2.)))
    #verify if there is a possible factor of 2 in the value found for Dnu
    if roundfac == 0:
        pass
    elif roundfac == -1:
        if verbose: print("Dnu divided by 2 for compatibility with numax")
        Dnu_eacf /= 2
        status += -10
    elif roundfac == 1:
        if verbose: print("Dnu multiplied by 2 for compatibility with numax")
        Dnu_eacf *= 2
        status += -20
    else:
        if verbose: print(f'Dnu is incorrect. Discrepancy from the scaling law by factor of {np.exp(lnfac)}')
        status += -30

    res = Dnu_eacf, numax_eacf, correl, status
    if verbose: print('Dnu: {:.2f} µHz, numax: {:.1f} µHz, maximum correlation {:.2f}  (status: {:0d})'.format(*res))

    return res
