import numpy as _np
import matplotlib.pyplot as _plt
import matplotlib.ticker as _mticker
from ..hough import load_lambda_tables, valid_k
from scipy.interpolate import make_interp_spline
from ..Freq import *
from ..common import color_tables

all = ['plot_stretch_rot']

def plot_stretch_rot(modes_obs, Pi0, rot, m, l=None, k=None,
                     size_field='amp', size=(2.5,6.5), size_ref=[None,None],
                     c_obs=None,
                     model=None, s_mod=6,
                     c_mod=None,
                     yunit='d', ylim=(None,None), ycorot=False, #yaxis: unit, ylim and corot or inertial
                     fold = None, #None is auto (only Rossby are folded)
                     ignore_identification = False,
                     ax=None, #if provided, must be an Axes where the plot is done
                     outputfile='',
                     single=False, single_shift=0.):
    """!plot a stretched echelle diagram of a rotating g mode pulsator
    @param modes_obs ModeSet|tuple(ModeSet): set of modes/frequencies to be plot as observations
    @param Pi0 Freq|float: Buoyancy radius. If float, it is assumed to be in seconds
    @param rot Freq|float: stellar rotation. If float, it is assumed to be in µHz
    @param m integer: azimuthal order used to plot the diagram
    @param k integer|None: index k of the mode series (k or l must be provided)
    @param l integer|None: degree l of the mode series (k or l must be provided)
    @param model None|ModeSet|tuple(ModeSet): set of modes/frequencies to be plot as a comparison model
    @param yunit str: valid unit (in Freq.unit_list) to plot the y axis (default: 'd')
    @param ycorot bool: If true frequencies (periods) in the corotating frame are plotted on the y axis (default: False)
    @param ax None|Axes: pyplot axis where diagram is plotted. If None a new figure is made
    @param outputfile str: If not empty, name of the file where the figure is saved (ignored if ax is provided)
    """

    k = valid_k(m,k,l)
    l=abs(m)+k
    s,lamb = load_lambda_tables(m,k=k,l=l)
    bspl_lamb = make_interp_spline(s, lamb, k=3)

    str_rot=str(rot)

    if isinstance(Pi0, Freq):
        Pi0 = Pi0.getv('s')

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

    ax.set_title('rotation:'+str_rot,fontsize='medium')

    for imode in range(nset):
        modes=modes_obs[imode]

        modes.to_frame('in') #ensure frequency are in the inertial frame
        modes.set_rot(rot)   #set the assumed rotation
        if(_np.all(modes.get('m')==None) or ignore_identification):
            modes.set_mlk(m, l=l, k=k) # set the assumed identification
        else: #keep only relevant identifications
            ind_ok=(modes.get('m')==m)&(modes.get('l')==l)
            if not _np.any(ind_ok):
                if isobs[imode]:
                    iobs+=1
                else:
                    imod+=1
                continue
            else:
                modes=modes[ind_ok]

        yunit=Freq.clean_unit(yunit)
        if not ycorot: y=modes.getv(yunit) #y in inertial frame
        s_modes = modes.gets()
        lamb_modes = bspl_lamb(s_modes)
        modes.to_frame('co',folding=fold)
        if ycorot: y=modes.getv(yunit) #y in corot frame
        Pco, ePco = modes.getve('s')

        Pstretch = Pco * _np.sqrt(lamb_modes)
        x=Pstretch%Pi0

        if isobs[imode]:
            ePstretch = ePco * _np.sqrt(lamb_modes)
            ex=ePstretch
            vec_size=_np.array(modes.get(size_field),float)
            vec_size[~(vec_size>0.)]=0.
            if _np.count_nonzero(vec_size) > 0:
                meds=_np.median(vec_size[vec_size>0.])
                vec_size[vec_size==0.]=meds
                if size_ref[0] is None:
                    size_ref[0]=min(vec_size)
                    size_ref[1]=max(vec_size)
                vec_size=(vec_size-size_ref[0])/(size_ref[1]-size_ref[0])*(size[1]**2-size[0]**2)+size[0]**2
            else:
                vec_size[:]=(size[0]+size[1])/2
                vec_size**=2

            ax.scatter(x, y, s=vec_size, c=c_obs[iobs%n_cobs])
            ax.scatter(x+Pi0, y, s=vec_size, c=c_obs[iobs%n_cobs])
            ax.errorbar(x, y, ls='', c=c_obs[iobs%n_cobs], xerr=ex)
            ax.errorbar(x+Pi0, y, ls='', c=c_obs[iobs%n_cobs], xerr=ex)
            iobs+=1
        else:
            ax.plot(x,y,ms=s_mod,c=c_mod[imod%n_cmod],marker='o', ls='', mfc='none')
            ax.plot(x+Pi0,y,ms=s_mod,c=c_mod[imod%n_cmod],marker='o', ls='', mfc='none')
            imod+=1

    if single:
        ax.set_xlim(single_shift,single_shift+Pi0)
    else:
        ax.set_xlim(0,2*Pi0)
        ax.axvline(x=Pi0,ls=':',c='k')
    ax.set_ylim(ylim)

    if k<0:
        mode_label=f'm={m},k={k}'
    else:
        mode_label=f'm={m},l={k+abs(m)}'

    frame_label='co' if ycorot else 'in'

    ax.set_xlabel(rf'$\sqrt{{\Lambda}}_{{{mode_label}}} P_{{\rm co}}$ mod $\Pi_0$ ({Pi0:.0f} s)')
    is_freq = yunit in Freq.unit_f_list
    var_label=r'\nu' if is_freq else 'P'
    ax.set_ylabel(rf'${var_label}_{{\rm {frame_label}}}$ ({yunit})')

    ax2=ax.twinx() #a second axis for spin parameter
    ax2.set_ylabel(rf's({mode_label})')
    ax2.set_ylim(ax.get_ylim())
    formatter = _mticker.FuncFormatter(lambda y, pos: f'{Mode(y,yunit,m=m,k=k,rot=rot,corot=ycorot,folded=fold).gets():.1f}')
    ax2.yaxis.set_major_formatter(formatter)

    if show_plot:
        fig.tight_layout()
        if save_plot:
            fig.savefig(outputfile)
        else:
            _plt.show()
