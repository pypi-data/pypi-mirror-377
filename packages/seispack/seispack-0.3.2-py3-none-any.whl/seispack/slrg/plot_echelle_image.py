import numpy as np
import matplotlib.pyplot as _plt
from ..basic import rebin
from ..PSD import PSD
from .scaling_law import numax_from_Dnu
from ..Freq import ModeSet

def plot_echelle_image(spectrum, Dnu, numax=None, *,
                        nrange=None, nushift=0.,
                        rebin_factor=0,
                        smooth='Epanechnikov', smooth_window=None, qplot=0.97,
                        ax=None, #if provided, must be an Axes where the plot is done
                        outputfile='', #if provided, must be an Axes where the plot is done
                        model=None):
    """
    plot an echelle diagramme as an image from a power spectrum
    """

    if isinstance(spectrum, PSD):
        spectrum.to_xunit('µHz')
        nu=spectrum.x
        sp=spectrum.y
    else:
        nu=spectrum[0]
        sp=spectrum[1]

    binsize=nu[1]-nu[0]

    if rebin_factor is None:
        rebin_factor=1
    elif rebin_factor < 1: #if automatic: less than 1000 points in x direction
        rebin_factor=max(1,round(Dnu/binsize/1000))

    if numax is None: numax=numax_from_Dnu(Dnu)

    if nrange is None:
        nrange=(-6,6) if Dnu < 30. else (-11,11)


    if smooth_window is None:
        smooth_window=7. if Dnu < 30. else 21

    window=2*(round(max(1,smooth_window)+1)//2)-1
    nmax=round(numax/Dnu)
    nu0=max(nu.min(),(nmax+nrange[0])*Dnu+nushift)
    nu1=min(nu.max(),(nmax+nrange[1])*Dnu+nushift)
    window_nu=window*binsize


    if smooth == None or smooth == 'None' or smooth_window==1:
        spc=sp
        print("No smoothing")
    else:
        if smooth =='Epanechnikov':
            Kernel=1-(2*(np.arange(1,window+1))/(window+1)-1)**2
            print("Epanechnikov smoothing, window=",window,window_nu)
        elif smooth =='Hanning':
            Kernel=np.hanning(window)
            print("Hanning smoothing, window=",window,window_nu)
        else:
            Kernel=np.ones(window)
            print("Carbox smoothing, window=",window,window_nu)
        Kernel=Kernel/Kernel.sum()
        spc=np.convolve(sp,Kernel,mode='same')

    npt0=sp.size
    if(rebin_factor > 1):
        spr=rebin(spc, rebin_factor)
        nur=rebin(nu, rebin_factor)
        print("Rebinning factor:",rebin_factor)
    else:
        spr=spc
        nur=nu
        print("No rebinning")

    binsizer=nur[1]-nur[0]
    nptr_Dnu=round(Dnu/binsizer)
    Dnur=binsizer*nptr_Dnu

    i0=round((nu0-nur[0])/binsizer)
    nu0r=i0*binsizer
    norder=round((nu1-nu0r)/Dnur)
    i1=i0+norder*nptr_Dnu
    if (i1>nur.size):
        i1=i1-nptr_Dnu
        norder=norder-1

    imr=spr[i0:i1].reshape(norder,nptr_Dnu)

    x = np.arange(nptr_Dnu)*binsizer
    y = nur[i0:i1:nptr_Dnu]+0.5*Dnur

    vmax=np.quantile(imr,qplot)
    print("(max, {q:.1f}%) = ({m:.3g}, {v:.3g})".format(q=qplot*100,m=imr.max(),v=vmax))

    show_plot=ax is None
    if show_plot:
        fig, ax = _plt.subplots()
        save_plot=outputfile != ''

    ax.pcolormesh(x,y,imr,vmin=0,vmax=vmax)
    ax.set_xlabel(fr'$\nu$ mod $\Delta\nu$ ({Dnur:.2f} $\mu$Hz)')
    ax.set_ylabel(r'$\nu$ ($\mu$Hz)')


    symbol_list=['v','o','s','x']
    if model is not None:
        numodel=model.getv('µHz')
        indmodel=(numodel>nu0)&(numodel<nu1)
        ymodel=numodel[indmodel]
        xmodel=(numodel[indmodel]-nu0r)%Dnu
        lmodel=model[indmodel].get('l')
        for l in range(len(symbol_list)):
            indl=lmodel==l
            if any(indl):
                ax.scatter(xmodel[indl],ymodel[indl],marker=symbol_list[l],c='red')

    if show_plot:
        fig.tight_layout()
        if save_plot:
            fig.savefig(outputfile)
        else:
            _plt.show()
