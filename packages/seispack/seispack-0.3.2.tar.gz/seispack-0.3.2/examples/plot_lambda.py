import numpy as np
import matplotlib.pyplot as plt
import seispack.hough as hg

# build a new table
vmiss=-1.0e99
lam, eta, kt, mt = hg.make_tabulated_lambda(spin=(-50,50,0.2),m=(-3,0),k=(-4,4),optim_nt=True, missing=vmiss)
neta=eta.size
nk=kt.size
nm=mt.size
iref=35 # reference index for plotting label

lam=np.ma.masked_values(lam, vmiss) #mask missing values

for im,m in enumerate(mt): # generate one figure for each m
    fig, ax = plt.subplots()
    ax.axhline(y=0,c='k',lw=0.7) #add a horizontal axis y=0
    ax.axvline(x=0,c='k',lw=0.7) #add a vertical axis x=0
    for ik,k in enumerate(kt):
        c='r' if (k<0) else 'b' #color red for k<0, blue for >=0
        ls='--' if (k%2) else '-' #solid / dashed line for even/odd k
        ax.plot(eta,lam[:,ik,im],c=c,ls=ls)
        iplot=iref if k<0 else -iref
        if((k>0 and m==0) or (m<0 and k>=-2)):
            ax.text(eta[iplot], lam[iplot,ik,im],
                    rf'$k={k:0d}$',
                    c=c, ha='center', va='center',
                    bbox=dict(pad=0.1, color=('w',0.7))
                    )
    ax.set_xlabel(r'$\eta=2\Omega/\omega$')
    ax.set_xlim(min(eta),max(eta))
    ax.set_ylabel(rf'$\Lambda_{{{m:0d},k}}$')
    ax.set_title(fr'$m={m:0d}$')
    hg.util.set_scaleLS(ax) #define a log scale as in Lee & Saio 1997
    ax.set_ylim(-5,)
    fig.tight_layout()
    fig.savefig(f'lambda_m{m:0d}.pdf')
