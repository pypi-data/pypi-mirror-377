import numpy as _np
import matplotlib.pyplot as _plt
from ..Freq import *
from ..common import color_tables

def plot_echelle(modes_obs, Dnu, nushift=0., *,
                    size_field='amp', size=(2.5,6.5),
                    c_obs=None,
                    model=None, s_mod=6,
                    c_mod=None,
                    l_symlist=['v','o','s','^'],
                    unit='µHz', ylim=(None,None),
                    ax=None, #if provided, must be an Axes where the plot is done
                    title=None,
                    outputfile=''): #if provided, must be an Axes where the plot is done

    """
    plot an echelle diagramme from a ModeSet
    """

    if isinstance(Dnu, Freq):
        Dnu = Dnu.getv(unit)

    if(isinstance(modes_obs, ModeSet)):
        modes_obs=(modes_obs,)

    nset=len(modes_obs)
    isobs=[True]*nset

    if model is not None:
        if(isinstance(model, ModeSet)):
            model=(model,)
        nset_model=len(model)
        isobs+=[False]*nset_model
        nset+=nset_model
        modes_obs+=model

    iobs=0
    imod=0

    c_obs, c_mod = color_tables(c_obs, c_mod)
    n_cobs=len(c_obs)
    n_cmod=len(c_mod)

    show_plot=ax is None
    if show_plot:
        fig, ax = _plt.subplots()
        save_plot=outputfile != ''

    if title is not None: ax.set_title(title)

    lmax=len(l_symlist)-1

    for imode in range(nset):
        modes=modes_obs[imode]
        nu, enu = modes.getve(unit)
        l = modes.get('l')
        mask_none=l==None
        if _np.all(mask_none):
            l[:]=1
        elif _np.any(mask_none):
            l[mask_none]=lmax
        l[l>lmax]=lmax
        y=nu
        x=(nu+nushift)%Dnu
        ex=enu

        if isobs[imode]:
            vec_size=_np.array(modes.get(size_field),float)
            vec_size[~(vec_size>0.)]=0.
            if _np.count_nonzero(vec_size) > 0:
                meds=_np.median(vec_size[vec_size>0.])
                vec_size[vec_size==0.]=meds
                vec_size=(vec_size-min(vec_size))/(max(vec_size)-min(vec_size))*(size[1]**2-size[0]**2)+size[0]**2
            else:
                vec_size[:]=(size[0]+size[1])/2
                vec_size**=2

            for l0 in range(lmax+1):
                indl=l==l0
                ax.scatter(x[indl], y[indl], s=vec_size[indl], c=c_obs[iobs%n_cobs], marker=l_symlist[l0])
                ax.errorbar(x[indl], y[indl], ls='', c=c_obs[iobs%n_cobs], xerr=ex[indl])
            iobs+=1
        else:
            for l0 in range(lmax+1):
                indl=l==l0
                ax.plot(x[indl],y[indl],ms=s_mod, mfc='none',mec=c_mod[imod%n_cmod],marker=l_symlist[l0], ls='')
            imod+=1

    ax.set_xlim(0,Dnu)
    ax.set_xlabel(fr'$\nu$ mod $\Delta\nu$ ({Dnu:.2f} {unit})')
    ax.set_ylabel(fr'Frequency ({unit})')

    if show_plot:
        fig.tight_layout()
        if save_plot:
            fig.savefig(outputfile, dpi=200)
        else:
            _plt.show()
