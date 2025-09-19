import numpy as np
from ..PSD import PSD

def bg_proxy(spectrum, nbox=100, w=(0.66,0.88)):
    """Background proxy taken for the median
    it is divided ln(2) to recover the mean
    (after PLATO pipeline)
    """

    xunit=spectrum.xunit
    spectrum.to_xunit('µHz')

    nu=spectrum.x
    sp=spectrum.y
    yunit=spectrum.yunit


    nu_box = np.linspace(np.log(nu[1]), np.log(nu[-1]), nbox)
    nu_box = np.exp(nu_box)

    m=[ np.median(sp[abs(nu-nui)<w[0]*nui**w[1]]) for nui in nu_box ]

    bg=np.interp(nu,nu_box,m) / np.log(2.)

    bg=PSD(nu,bg,xunit='µHz',yunit=yunit)

    # convert in original unit
    bg.to_xunit(xunit)
    spectrum.to_xunit(xunit)

    return bg

def normalise_to_noise(spectrum, background=None):
    """Normalise the spectrum with the background. If not provided,
    it is estimated from the median.
    """
    if background is None:
        background=bg_proxy(spectrum)

    background.to_xunit(spectrum.xunit)

    if(background.yunit != spectrum.yunit):
        raise ValueError(f'background and spectrum have different units {background.yunit} != {spectrum.yunit}')

    s_n=spectrum.y/background.y

    s_n=PSD(spectrum.x, s_n, spectrum.xunit, 'S/N')

    return s_n