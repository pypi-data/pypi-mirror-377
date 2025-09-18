import numpy as np

__all__ = [ 'psd' ]

def psd(x, dt, *, over=1, verbose=True):
    """!
    computed the calibrated one-sided psd of x on the interval [0, Nyquist frequency]
    @param x: array including the evenly sampled time series. 0 are treated as missing data
    @param dt: time step
    @param over: oversampling factor (default: 1)
    @param verbose: boolean controlling the verbose mode (default: True)
    """
    nx=x.size

    if over>1:
        y = np.pad(x,(0,(over-1)*nx))
        ny = nx * over
    else:
        y = x
        ny = nx

    nzero=y.nonzero()[0]
    #nok=np.count_nonzero(y)
    nok=nzero.size
    nTtot=nzero[-1]-nzero[0]+1
    Ttot=dt*nTtot

    dnu = 1./(ny*dt)

    facfil=ny/nok

    ny2=ny//2+1

    sp=abs(np.fft.fft(y)[:ny2])**2
    sp[1:-1] *= 2.
    if ny%2!=0: sp[-1] *= 2.

    if verbose: print(f'filling factor={1/facfil}, ny={ny}, nx={nx}, nok={nok}, nTtot={nTtot}')
    #print(f'facfil={facfil} Parceval (one-sided PSD) = ',(x**2).sum(),sp.sum()/ny)
    #sp = sp/(nok**2*over*dnu)
    sp = sp/nok**2*Ttot
    nu = np.arange(ny2)*dnu

    return nu,sp
