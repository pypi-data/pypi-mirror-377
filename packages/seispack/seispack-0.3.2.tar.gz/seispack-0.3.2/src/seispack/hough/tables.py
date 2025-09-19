from .core import *
from .util import resolution_estimate, valid_k
import numpy as _np
from tqdm import tqdm as _tqdm
from pathlib import Path as _Path
import importlib_resources as _importlib_resources
_hough_resources=_importlib_resources.files("seispack.hough")

tables_path = _hough_resources.joinpath("tables")

__all__=['make_tabulated_lambda',
         'save_tabulated_lambda',
         'generate_lambda_ascii_tables',
         'generate_package_lambda_ascii_tables',
         'load_lambda_tables_m',
         'load_lambda_tables',
         'tables_path']

def make_tabulated_lambda(nt=512, spin=(0,50,0.01),
                          m=(-3,3), k=(-3,3), prograde_negative=True,
                          optim_nt=False, missing=-1e99):
    """!
    generate tables of lambda for a range of spin parameters and k, for different m
    @param nt: int resolution used in the latitudinal direction (default: 512)
    @param spin: tuple(int,int,int) maximal spin parameter and grid step (default: 0,50,0.01), or a list
    @param m: tuple(int,int) tables are generated for azimuthal order m[0] to m[1] (default: -3,3), or a list
    @param k: [int,int] range of k written as columns in the generated files (default: [-3,3])

    missing values (i.e. k<0 for |s|<1) are set to -1e99
    """

    if isinstance(spin, tuple):
        match len(spin):
            case 3:
                ne=round((spin[1]-spin[0])/spin[2])+1
                etat=_np.linspace(spin[0],spin[1],ne)
            case 2:
                if spin[1]<spin[0]:
                    ne=round(spin[0]/spin[1])+1
                    etat=_np.linspace(0.,spin[0],ne)
                else:
                    ne=101
                    etat=_np.linspace(spin[0],spin[1],ne)
            case _:
                raise ValueError(f'tuple has {len(spin)} elements, 2 or 3 expected')
    elif isinstance(spin, (range, list,_np.ndarray)):
        etat=_np.array(spin).flatten()
    ne=etat.size

    if isinstance(m, tuple):
        match len(m):
            case 3: mt=_np.arange(m[0],m[1]+1,m[2])
            case 2: mt=_np.arange(m[0],m[1]+1)
            case _: raise ValueError(f'tuple has {len(spin)} elements, 2 or 3 expected')
    elif isinstance(m, (range, list,_np.ndarray)):
        mt=_np.array(m).flatten()
    nm=mt.size

    kmin,kmax=k
    if kmax<kmin:
        print("kmin>kmax in range - aborted")
        return
    kt=_np.arange(kmin,kmax+1)
    nk=kt.size

    lamb=_np.full((ne,nk,nm), missing)

    for ie in _tqdm(range(ne)):
        if(prograde_negative):
            eta=etat[ie]
        else:
            eta=-etat[ie]
        for im in range(nm):
            m=mt[im]
            if optim_nt:
                nt=0
                for k in kt:
                    nt=max(nt,resolution_estimate(eta,m,k))
            for odd in [0,1]:
                S=Spectrum(MatWi(m,odd,eta,nt=nt),kmin=kmin,kmax=kmax, verbose=False)
                for ik in range(nk):
                    k=kt[ik]
                    val=S.lamb[S.k==k]
                    if val.size==1:
                        lamb[ie,ik,im]=val.squeeze()
                    if(k==0 and m==0): lamb[ie,ik,im]=0


    return lamb, etat, kt, mt

def save_tabulated_lambda(lambda_table, spin_table, k_table, m_table, fileroot='lambda',outdir=''):

    """
    write tables of lambda in ascii files for different m
    @param lambda_table array(ns,nk,nm) lambda for different spin parameters, k and m
    @param spin_table array(ns) of spin parameters
    @param k_table array(nk) of k
    @param m_table array(nm) of m
    @param fileroot: str tables are stored in files '{fileroot}_m{m}.txt' (default: lambda)
    @param outdir: Path or str directory where files are written (default: '')
    """

    path = _Path(outdir)
    nm=m_table.size
    ns=spin_table.size
    nk=k_table.size

    for im in range(nm):
        filename=f'{fileroot}_m{m_table[im]:0d}.txt'
        with open(path/filename, "w") as file:
            file.write(r"# eta \ k")
            file.write((nk*" {:8d}         ").format(*k_table))
            file.write("\n")
            for ie in range(ns):
                file.write(" {:7.3f} ".format(spin_table[ie]))
                for ik in range(nk):
                    file.write(" {:17.10e}".format(lambda_table[ie,ik,im]))
                file.write("\n")

    return

def generate_lambda_ascii_tables(fileroot='lambda',outdir='', nt=1024, spin=(0,100,0.01),
                          m=(-3,3), k=(-3,3), prograde_negative=True,
                          optim_nt=False):

    save_tabulated_lambda( *make_tabulated_lambda(nt, spin, m, k, prograde_negative, optim_nt),
                          fileroot, outdir)




def generate_package_lambda_ascii_tables():
    generate_lambda_ascii_tables(outdir=tables_path)


def load_lambda_tables_m(m,fileroot='lambda',outdir=None):
    if(outdir is None): outdir=tables_path
    outdir=_Path(outdir)
    filename=f'{fileroot}_m{m:0d}.txt'
    with open(outdir/filename, 'rt') as f:
        h=f.readline()
        res=_np.loadtxt(f)
    s=res[:,0]
    lamb=res[:,1:]
    k=_np.fromstring(h[10:],sep=' ')
    return lamb, s, k



def load_lambda_tables(m,*,k=None, l=None, fileroot='lambda',outdir=None):

    k = valid_k(m,k,l)

    lamb, s_tab, k_tab = load_lambda_tables_m(m,fileroot,outdir)

    ik=_np.argwhere(k_tab==k).squeeze()

    match ik.size:
        case 1: return s_tab, lamb[:,ik]
        case 0:
            print(f'table not found for m={m}, k={k}')
            return None
        case _: raise TypeError('ik must be an scalar here!')
