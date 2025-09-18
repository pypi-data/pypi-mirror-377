from ..Freq import Freq
lawe=0.791 # exponent of the scaling relation between Dnu and numax in µHz
lawc=0.233 # factor of the relation: Dnu ~ lawc*numax**lawe

__all__ = [' Dnu_from_numax','numax_from_Dnu']

def Dnu_from_numax(numax):

    if(isinstance(numax, Freq)):
        Dnu_val=lawc*(numax.getv('muHz'))**lawe
        Dnu=Freq(Dnu_val,'muHz')
    else: #assumed µHz
        Dnu=lawc*numax**lawe

    return Dnu

def numax_from_Dnu(Dnu):
    ex=1./lawe
    con=(1./lawc)**ex

    if(isinstance(Dnu, Freq)):
        nu_val=con*(Dnu.getv('muHz'))**ex
        numax=Freq(nu_val,'muHz')
    else: #assumed µHz
        numax=con*Dnu**ex

    return numax