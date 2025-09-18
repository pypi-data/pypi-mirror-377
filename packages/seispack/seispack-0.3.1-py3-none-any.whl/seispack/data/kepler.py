from numbers import Number
import numpy as np
from os import getenv
from pathlib import Path
from astroquery.mast import Observations
from astropy.io import fits
from ..PSD import PSD, LightCurve

__all__ = ['download_kepler', 'download_kepseismic', 'read_kepseismic_psd', 'read_kepseismic_lc', 'read_kadacs_lc', 'read_kadacs_psd']


def download_kepler(kic, cadence='all', type='lc', *, preview=True, report=True, forced=False, verbose=True):
    """! download from MAST Kepler data. Locally, it is put in the directory contained in the environment
    variable SEISPACK_DATA.
    @param kic int: Kepler Id (one star or a list of stars)
    @param cadence str: short cadence ('sc'), long cadence ('lc') or both ('all', default)
    @param type str: lightcurve ('lc', default) or pixel data ('pd')
    @param preview bool: download also preview png files if any (default: True)
    @param report bool: download also pdf reports if any (default: True)
    @param forced bool: download the data even if they are already locally existing (Default: False)
    @param verbose bool: verbose mode (Default: True)
    """

    datapath = getenv('SEISPACK_DATA','')
    datapath = Path(datapath)

    if isinstance(kic, (list, tuple, np.ndarray)):
        starname=[f'kplr{k:09d}' for k in kic]
    else:
        starname=[f'kplr{kic:09d}']


    obs_table=Observations.query_criteria(target_name=starname, obs_collection='Kepler')

    if len(obs_table)==0:
        print('no data found')
        return

    where_lc=np.array(['_lc_' in x for x in obs_table['obs_id']])
    where_sc=np.array(['_sc_' in x for x in obs_table['obs_id']])
    if cadence.lower() == 'lc':
        obs_table=obs_table[where_lc]
    elif cadence.lower() == 'sc':
        obs_table=obs_table[where_sc]
    else:
        obs_table=obs_table[where_sc|where_lc]

    if len(obs_table)==0:
        print('no data available')
        return
    elif verbose:
        print(obs_table)

    products = Observations.get_product_list(obs_table)

    typefile_list=[]
    if preview: typefile_list+=['.png']
    if report: typefile_list+=['.pdf']
    if type == 'lc':
        datatype='lc.fits'
    elif type == 'pd':
        datatype='pd-targ.fits'
    else:
        print(f"unknown type {type} ('lc' or 'pd' expected)")
        return
    if cadence.lower() == 'lc' or cadence.lower() == 'all':
        typefile_list+=['_l'+datatype]
    if cadence.lower() == 'sc' or cadence.lower() == 'all':
        typefile_list+=['_s'+datatype]


    if len(typefile_list)==0:
        print('no data requested...')
        return
    elif verbose:
        print(typefile_list)
    file_list=[]
    for filename in products['productFilename']:
        isfile=False
        for tag in typefile_list: isfile= isfile or (tag in filename)
        if isfile: file_list.append(filename)

    print(f'{len(file_list)} files found.')

    _ = Observations.download_products(products,
                                       productFilename=file_list,
                                       download_dir=datapath,
                                       cache=not forced,
                                       verbose=verbose)



def download_kepseismic(kic:int, filter_d=20, data_type='psd', preview=True, forced=False, verbose=True):
    """! download from MAST the KEPSEIMIC data locally in the directory contained in the environment
    variable SEISPACK_DATA.
    @param kic int: Kepler Id of the star
    @param filter_d int: filters in days 20, 55 or 80. 'all' will download everything
    @param type str: lightcurve ('lc'), power spectrum density ('psd', default) or both ('all') or none ('none')
    @param preview bool: download also the preview png (default: True)
    @param forced bool: download the data even if they are already locally existing (Default: False)
    @param verbose bool: verbose mode (Default: True)

    @remark Note about KEPSEISMIC data (extracted from https://archive.stsci.edu/prepds/kepseismic/)
    HLSP Authors: Savita Mathur, Ângela Santos, Rafael A. García
    KEPSEISMIC light curves are obtained from Kepler pixel-data files using large custom apertures
    that produce more stable light curves on longer time scales for seismic studies.
    The resultant light curve is processed through the implementation of the Kepler Asteroseismic Data Analysis
    and Calibration Software (KADACS, García et al. 2011). KADACS corrects for outliers, jumps, and drifts,
    properly concatenates the independent Kepler Quarters in a star-by-star basis.
    It also fills the gaps shorter than 20 days in long cadence data following in-painting techniques based
    on a multi-scale cosine transform (García et al. 2014, Pires et al. 2015).
    The resulting light curves are high-pass filtered at 20, 55 days (quarter by quarter)
    and 80 days (using the full light curve at once) yielding three different light curves for each target.
    For light curves longer than one month, KADACS corrects for discontinuities at the edges of the Kepler Quarters.
    Refer to the full set of KEPSEISMIC observations using the DOI doi:10.17909/t9-mrpw-gc07.
    This work was funded by the NASA grant NNX17AF27G.
    References:
        - García et al., 2011, MNRAS, 414, L6
        - García et al., 2014, A&A, 568, 10
        - Pires et al., 2015, A&A, 574, 18
    """

    datapath = getenv('SEISPACK_DATA','')
    datapath = Path(datapath)

    if isinstance(kic, (list, tuple, np.ndarray)):
        starname=[f'kplr{k:09d}' for k in kic]
    else:
        starname=[f'kplr{kic:09d}']


    obs_table=Observations.query_criteria(target_name=starname,
                                          obs_collection='HLSP',
                                          provenance_name='KEPSEISMIC')

    #selected table with the wanted high-pass filter (if any)
    if isinstance(filter_d, Number):
        filter_name=f'-{int(filter_d):0d}d_'
        obs_table=obs_table[[filter_name in x for x in obs_table['obs_id']]]

    if len(obs_table)==0:
        print('no data available')
        return
    elif verbose:
        print(obs_table)

    products = Observations.get_product_list(obs_table)

    #selected files with psd, lc, preview
    tag_list=['_preview'] if preview else []
    data_type=data_type.lower()
    if(data_type == 'lc'  or data_type == 'all'): tag_list+=['_cor-filt-inp']
    if(data_type == 'psd' or data_type == 'all'): tag_list+=['_cor-psd-filt-inp']

    if len(tag_list)==0:
        print('no data requested...')
        return
    elif verbose:
        print(tag_list)

    file_list=[]
    for filename in products['productFilename']:
        isfile=False
        for tag in tag_list: isfile= isfile or (tag in filename)
        if isfile: file_list.append(filename)

    print(f'{len(file_list)} files found.')

    _ = Observations.download_products(products,
                                       productFilename=file_list,
                                       download_dir=datapath,
                                       cache=not forced,
                                       verbose=verbose)


def read_kepseismic(kic, filter_d=20, psd=True, *, auto_load=True, mastpath=None):

    """! read KEPSEIMIC light curve (LC) or power spectrum density (PSD) FITS files
    @param kic int: Kepler Id of the star
    @param filter_d int: filters in days 20 (default), 55 or 80.
    @param psd bool: If True (default), the function returns the PSD, else it returns LC.
    @param auto_load bool: If True (default), the files are download from the MAST if absent locally
    @param mastpath: If provided, it should be a string (or a Path type object) containing the
                    directory where the file is located. If not provided, the file is assumed to be
                    in $SEISPACK_DATA/mastDownload/HLSP
    @return a tuple (x, y, xunit, yunit, h), where
        x is an array of time (for LC) or frequency (for PSD)
        y is an array of flux (for LC) or spectral density (for PSD)
        xunit is a string containing the unit of x (days or Hz)
        yunit is a string containing the unit of y (ppm or ppm2/µHz)
        h contains the header of the FITS file

    """
    if mastpath is None:
        datapath = getenv('SEISPACK_DATA','')
        datapath = Path(datapath)
        mastpath = datapath/'mastDownload/HLSP'
    mastpath = Path(mastpath)

    file_id=f'kplr{kic:09d}-{int(filter_d):02d}d'
    subdir=f'hlsp_kepseismic_kepler_phot_{file_id}_kepler_v1_cor-filt-inp'
    str_psd='-psd' if psd else ''
    filename=f"hlsp_kepseismic_kepler_phot_{file_id}_kepler_v1_cor{str_psd}-filt-inp.fits"
    filepath=mastpath/subdir

    if not (filepath/filename).exists():
        print("file does not exist in the specified directory...", end=" ")
        if auto_load:
            print("looking on MAST...")
            data_type='psd' if psd else 'lc'
            download_kepseismic(kic,filter_d,data_type)
        if not (filepath/filename).exists():
            raise Exception("file not found. Aborted")

    with fits.open(filepath/filename) as hdul:
        h = hdul[0].header
        x = hdul[1].data['TIME'].astype('float')
        y = hdul[1].data['FLUX'].astype('float')

    if psd:
        xunit='Hz'
        yunit='ppm2/µHz'
    else:
        xunit='d'
        yunit='ppm'

    return x, y, xunit, yunit, h

def read_kepseismic_psd(kic, filter_d=20, **kwargs):
    return PSD(*read_kepseismic(kic, filter_d, True, **kwargs))

def read_kepseismic_lc(kic, filter_d=20, **kwargs):
    return LightCurve(*read_kepseismic(kic, filter_d, False, **kwargs))

def read_kadacs(kic, psd=True, *, path=None):

    """! read KADACS light curve (LC) or power spectrum density (PSD) FITS files
    @param kic int|filename: Kepler Id of the star or filename
    @param psd bool: If True (default), the function returns the PSD, else it returns LC.
    @param path: If provided, it should be a string (or a Path type object) containing the
                    directory where the file is located. If not provided, the file is assumed to be
                    in $SEISPACK_DATA
    @return a tuple (x, y, xunit, yunit, h), where
        x is an array of time (for LC) or frequency (for PSD)
        y is an array of flux (for LC) or spectral density (for PSD)
        xunit is a string containing the unit of x (days or Hz)
        yunit is a string containing the unit of y (ppm or ppm2/µHz)
        h contains the header of the FITS file

    """
    if path is None:
        datapath = getenv('SEISPACK_DATA','')
        path = Path(datapath)/'KADACS'
    path = Path(path)

    if isinstance(kic,Number):
        file_id=f'kplr{kic:09d}'
        str_psd='_PSD' if psd else ''
        filemask=f"{file_id}_*_COR{str_psd}_filt_inp.fits"
        file_list=[]
        for file in Path.glob(path,filemask): file_list.append(file)
        if len(file_list) == 0:
            print("file does not exist in the specified directory...", end=" ")
            raise Exception("file not found. Aborted")
        else:
            filename=path/file_list[0]
            print(filename)

    else:
        filename=Path(kic) #assumed filename is given

    if not (filename).exists():
        print("file does not exist in the specified directory...", end=" ")
        raise Exception("file not found. Aborted")

    with fits.open(filename) as hdul:
        h = hdul[0].header
        x = hdul[0].data[:,0].astype('float')
        y = hdul[0].data[:,1].astype('float')
        if psd:
            status=1
        else:
            status=hdul[1].data[:].astype('int')

    if psd:
        xunit='Hz'
        yunit='ppm2/µHz'
    else:
        xunit='d'
        yunit='ppm'

    return x, y, status, xunit, yunit, h

def read_kadacs_psd(kic, **kwargs):
    x, y, _, xunit, yunit, _ = read_kadacs(kic, True, **kwargs)
    return PSD(x, y, xunit, yunit)

def read_kadacs_lc(kic, **kwargs):
    x, y, status, xunit, yunit, _ = read_kadacs(kic, False, **kwargs)
    return LightCurve(x, y, xunit, yunit, extra={'status': status})