import numpy as _np
import matplotlib.pyplot as _plt
from ..Freq import *
from ..common import color_tables
from .stretch import tau_mod_Pi1

def plot_stretch(modes_obs, Pi1, par_p, q, *,
                    size_field='amp', size=(2.5,6.5),
                    c_obs=None,
                    model=None, s_mod=6,
                    c_mod=None,
                    yunit='µHz',
                    ylim=(None,None),
                    all_l=False,
                    ax=None, #if provided, must be an Axes where the plot is done
                    title=None,
                    outputfile=''): #if provided, must be an Axes where the plot is done

    """
    plot a stretched echelle diagramme from a ModeSet
    """

    xunit='s'
    #if xunit not in Freq.unit_P_list:
    #    raise ValueError(f'xunit must be a valid period unit: {xunit}. Valid units are {Freq.unit_P_list}')

    if not isinstance(Pi1, Freq): Pi1=Freq(Pi1, xunit) #if not specified Pi1 is assumed to be in xunit
    Pi1_x=Pi1.getv(xunit)

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

    for imode in range(nset):
        modes=modes_obs[imode]
        if not all_l: modes=modes[modes.get('l')==1]
        y = modes.getv(yunit)
        x, ex = tau_mod_Pi1(modes, Pi1, par_p, q, P_unit=xunit)


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
            ax.scatter(x, y, s=vec_size, c=c_obs[iobs%n_cobs], marker='o')
            ax.errorbar(x, y, ls='', c=c_obs[iobs%n_cobs], xerr=ex)
            ax.scatter(x+Pi1_x, y, s=vec_size, c=c_obs[iobs%n_cobs], marker='o')
            ax.errorbar(x+Pi1_x, y, ls='', c=c_obs[iobs%n_cobs], xerr=ex)
            iobs+=1

        else:
            ax.plot(x,y,ms=s_mod, mfc='none',mec=c_mod[imod%n_cmod],marker='o', ls='')
            ax.plot(x+Pi1_x,y,ms=s_mod, mfc='none',mec=c_mod[imod%n_cmod],marker='o', ls='')
            imod+=1


    ax.set_xlim(0,2*Pi1_x)
    ax.set_ylim(ylim)
    ax.axvline(x=Pi1_x,ls=':',c='k')


    ax.set_xlabel(fr'$\tau$ mod $\Delta\Pi_1$ ({Pi1_x:.2f} {xunit})')
    is_freq = yunit in Freq.unit_f_list
    var_label='Frequency' if is_freq else 'Period'
    ax.set_ylabel(f'{var_label} ({yunit})')

    if show_plot:
        fig.tight_layout()
        if save_plot:
            fig.savefig(outputfile, dpi=200)
        else:
            _plt.show()


    return
