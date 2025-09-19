"""!
Definition of various Classes useful to describe frequencies, modes and mode sets
it includes method for unit conversions and frame changes.
"""
from numbers import Number
import numpy as _np
import copy as _copy

__all__ = ['Freq', 'Mode', 'ModeSet']

class Freq:
    """!
    Class used to describe a frequency (or period) with a unit and an error
    it also include an extra dictionary for possible complementary information
    """
    unit_nu_list = ['Hz','mHz','µHz','nHz','c/d','adim','kHz','MHz','GHz']
    fac_nu = _np.array([1.,1e-3,1e-6,1e-9,1./86400.,1.,1e3,1e6,1e9])
    unit_nu_default = unit_nu_list[2] #µHz

    unit_om_list = ['rad/s','mrad/s','µrad/s','nrad/s']
    fac_om = _np.array([1.,1e-3,1e-6,1e-9])/(2.*_np.pi)
    unit_om_default = unit_om_list[0] #red/s

    unit_f_list = unit_nu_list + unit_om_list
    fac_f=_np.concatenate([fac_nu,fac_om])
    unit_f_default = unit_f_list[0] #Hz

    unit_P_list = ['s','ks','Ms','Gs','d','adimP','ms','µs','ns']
    fac_P = _np.array([1.,1e3,1e6,1e9,86400.,1.,1e-3,1e-6,1e-9])
    unit_P_default = unit_P_list[0] #s

    unit_list = unit_nu_list + unit_om_list + unit_P_list
    unit_default = unit_nu_default #µHz

    @classmethod
    def change_default(cls, unit):
        """! a class method to change the unit by default (µHz)"""
        unit=Freq.clean_unit(unit)
        if unit in Freq.unit_list:
            Freq.unit_default = unit
        else:
            print(unit,': unknown unit')
            print('valid units:', Freq.unit_list)

    def __init__(self, val, unit=None, *, err=None, norm=None, extra: dict=None):
        """!The Freq class initializer.
        @param val  The value of the frequency/period.
        @param unit The unit (default is Freq.unit_default, which is µHz by default).
            Valid units are :
                Hz, mHz, µHz, nHz, kHz, MHz, GHz, c/d,
                rad/s, mrad/s, µrad/s, nrad/s,
                s, ks, Ms, Gs, ms, µs, ns, d. µ can be written mu.
            Dimensionless frequency or period can be specified with adim and adimP.

        optional:
        @param err  The error of val
        @param norm A instance of the Freq class containing the normalization used to convert
            dimensionless quantity to/from unit quantity
        @param extra A dictionary containing extra information the user want to store

        @return  An instance of the Freq class.
        """
        if isinstance(val,Freq): #if the first argument is a Freq, the other are ignored and the attributes are copied, except extra
            self.val=val.val
            self.err=val.err
            self.unit=val.unit
            self.norm=val.norm
            if unit is not None:
                self.to(unit)
            if extra is None:
                self.extra=val.extra.copy()
            elif isinstance(extra, dict):
                self.extra=extra.copy()
            else:
                raise TypeError('extra must be a dictionary')
            return

        if unit is None: unit=Freq.unit_default
        self.unit = Freq.clean_unit(unit)

        if norm is None:
            self.norm = None
        else:
            self.norm = Freq(norm)

        if not isinstance(val, Number):
            raise TypeError('val must be a number')
        self.val = val

        if err is None:
            err=0.
        if isinstance(err, Freq):
            if err.unit[:4] == 'adim' or self.unit[:4] == 'adim':
                raise TypeError('err can be a Freq only if err and val in physical units to avoid mismatching normalization')
            if (err.unit in Freq.unit_f_list and self.unit in Freq.unit_f_list) or (err.unit in Freq.unit_P_list and self.unit in Freq.unit_P_list):
                err=err.getv(self.unit)
            else:
                val_unit_err = Freq.convert(self.unit,err.unit,val)
                _,err = Freq.convert(err.unit,self.unit,val_unit_err,err.val)
        if not isinstance(err, Number):
            raise TypeError('err must be a number at this point')
        self.err = err

        if extra is None:
            extra={}
        self.extra=extra.copy()


    def __str__(self):
        if self.err == 0.:
            err=''
        else:
            err=f' ± {self.err:.5g}'
        if(self.unit[:4] == 'adim' and self.norm is not None):
            str_norm=f'({self.norm})'
        else:
            str_norm=''
        return f'{self.val:.5g}{err} {self.unit}'+str_norm

    def __repr__(self):
        return 'Freq: '+str(self)

    @staticmethod
    def clean_unit(unit):
        unit=unit.replace('mu','µ')#.replace('/','')
        if unit not in Freq.unit_list:
            raise ValueError(f'unknown unit: {unit}. Valid units are {Freq.unit_list}')
        return unit

    @staticmethod
    def convert(unit_old, unit_new, val, err=None, norm=None):
        """!
        convert a frequency @param val and the error @param err in units @param unit_old
        into units @param unit_new.
        If one of the unit is dimensionless ('adim' for frequencies or 'adimP' for periods),
        the normalizing frequency @param norm: Freq must be provided
        """
        u_old=unit_old
        u_new=unit_new
        if ((unit_old[:4] == 'adim') ^ (unit_new[:4] == 'adim')):
            if(not isinstance(norm, Freq)):
                print('adimensional from/to physical units required a norm to be defined')
                print('norm:',norm)
                raise ValueError
            if unit_old[:4] == 'adim':
                if unit_old[4:]=='P':
                    u_old = Freq.unit_P_default
                else:
                    u_old = Freq.unit_f_default
                freq_norm = norm.getv(u_old)
                val = freq_norm * val
                if err is not None: err = freq_norm * err
            elif unit_new[:4] == 'adim':
                if unit_new[4:]=='P':
                    u_new = Freq.unit_P_default
                else:
                    u_new = Freq.unit_f_default
                freq_norm = norm.getv(u_new)
            else:
                raise Exception('should never occur!')

        if u_old in Freq.unit_f_list:
            iold = Freq.unit_f_list.index(u_old)
            if u_new in Freq.unit_f_list:
                inew = Freq.unit_f_list.index(u_new)
                val_new = val * Freq.fac_f[iold] / Freq.fac_f[inew]
                if err is not None:
                    err_new = err * Freq.fac_f[iold] / Freq.fac_f[inew]
            elif u_new in Freq.unit_P_list:
                inew = Freq.unit_P_list.index(u_new)
                val_new = 1. / (val * Freq.fac_f[iold]) / Freq.fac_P[inew]
                if err is not None:
                    err_new = err / val * val_new
            else:
                raise ValueError(f'unknown unit: {u_new}. Valid units are {Freq.unit_list}')

        elif u_old in Freq.unit_P_list:
            iold = Freq.unit_P_list.index(u_old)
            if u_new in Freq.unit_P_list:
                inew = Freq.unit_P_list.index(u_new)
                val_new = val * Freq.fac_P[iold] / Freq.fac_P[inew]
                if err is not None:
                    err_new = err * Freq.fac_P[iold] / Freq.fac_P[inew]
            elif u_new in Freq.unit_f_list:
                inew = Freq.unit_f_list.index(u_new)
                val_new = 1. / (val * Freq.fac_P[iold]) / Freq.fac_f[inew]
                if err is not None:
                    err_new = err / val * val_new
            else:
                raise ValueError(f'unknown unit: {u_new}. Valid units are {Freq.unit_list}')
        else:
            raise ValueError(f'unknown unit: {u_old}. Valid units are {Freq.unit_list}')

        if(u_new != unit_new):
            val_new = val_new / freq_norm
            if err is not None: err_new = err_new / freq_norm

        if err is not None:
            return val_new, err_new
        else:
            return val_new


    @staticmethod
    def frame_change(freq, frame_old, frame_new, rot, m, folding=False): #convention: prograde modes have negative m
        """
        if folding, be converting 'in' to 'co', one assume frequencies below m*rot are indeed negative
        """
        if not isinstance(freq, Freq):
            raise TypeError('freq must be an instance of Freq')
        if not isinstance(rot, Freq):
            raise TypeError('rot must be an instance of Freq')
        if(frame_old[:2] == frame_new[:2] or m == 0 or rot.val == 0.):
            res = freq.copy()
        elif(frame_old[:2] == 'co' and frame_new[:2] == 'in'):
            unit_ref = Freq.unit_nu_default
            res = freq.copy()
            res.to(unit_ref)
            rot_ref = rot.getv(unit_ref)
            valin = res.val - m * rot_ref #can be negative => folding still has to be catched
            res.val = valin
            res.to(freq.unit)
        elif(frame_old[:2] == 'in' and frame_new[:2] == 'co'):
            unit_ref = Freq.unit_nu_default
            res = freq.copy()
            res.to(unit_ref)
            mrot_ref = m*rot.getv(unit_ref)
            if(folding and m>0 and res.val<mrot_ref): # retrograde modes below mOmega => could be mode with frequency in corot below mHz
                valco = mrot_ref - res.val
            else:
                valco = res.val + mrot_ref #frequencies<0 in the corotating frame show are impossible, thus frequency<0 should be discarded afterwards
            res.val = valco
            res.to(freq.unit)
        else:
            raise ValueError('frame_old or frame_new unknown: '+str(frame_old)+', '+str(frame_new))
        return res

    def update(self, new):
        """update self from new, only with common attribute"""
        for key in self.__dict__:
            if hasattr(new, key):
                setattr(self, key, getattr(new, key))

    def set_err(self, err):
        if isinstance(err, Freq):
            if err.unit[:4] == 'adim' or self.unit[:4] == 'adim':
                raise TypeError('err can be a Freq, only where err and val are in physical units to avoid mismatching normalization')
            if (err.unit in Freq.unit_f_list and self.unit in Freq.unit_f_list) or (err.unit in Freq.unit_P_list and self.unit in Freq.unit_P_list):
                err=err.getv(self.unit)
            else:
                val_unit_err = Freq.convert(self.unit,err.unit,self.val)
                _,err = Freq.convert(err.unit,self.unit,val_unit_err,err.val)

        self.err = err

    def set_extra(self, key, val):
        self.extra[key]=val

    def get(self, key):
        if hasattr(self,key):
            return getattr(self,key)
        elif key in self.extra:
            return self.extra[key]
        else:
            return None

    def getve(self, unit=None, norm=None):
        """
        get the value of the frequency and the associated error.
        If unit is specified, the values are converted in the requested unit
        """
        if norm is None: norm=self.norm
        if unit is None:
            return self.val, self.err
        else:
            return Freq.convert(self.unit, Freq.clean_unit(unit), self.val, self.err, norm)

    def getv(self, unit=None):
        """
        get the value of the frequency.
        If unit is specified, the values are converted in the requested unit
        """
        val,_=self.getve(unit)
        return val

    def gete(self, unit=None):
        """
        get the value of the associated error.
        If unit is specified, the values are converted in the requested unit
        """
        _,err=self.getve(unit)
        return err

    def to(self, unit, norm=None):
        """
        change the unit of the value and the associated error of an instance of Freq
        """
        unit_new = Freq.clean_unit(unit)
        if(norm is not None): self.norm=norm
        self.val, self.err = Freq.convert(self.unit, unit_new, self.val, self.err, self.norm)
        self.unit = unit_new

    def add_f(self, freq, add_err=True):
        """
        add frequency
        """
        uold=self.unit
        if freq.unit not in Freq.unit_f_list:
            raise ValueError(f'freq must be a frequency, not a period {freq.unit=}')
        self.to(freq.unit)
        self.val+=freq.val
        if add_err: self.err=_np.sqrt(self.err**2 + freq.err**2)
        self.to(uold)

    def add_P(self, freq, add_err=True):
        """
        add Period
        """
        uold=self.unit
        if freq.unit not in Freq.unit_P_list:
            raise ValueError(f'freq must be a period, not a frequency {freq.unit=}')
        self.to(freq.unit)
        self.val+=freq.val
        if add_err: self.err=_np.sqrt(self.err**2 + freq.err**2)
        self.to(uold)





    def copy(self):
        return _copy.deepcopy(self)


class Mode(Freq):
    """
    Class used to described a oscillation mode. It is based on Freq with additional properties:
    - quantic numbers (n,l,m) (+k)
    - information on the rotation of the star
        + rot: Freq is rotation frequency/period)
        + corot: bool indicates if the frequency is expressed in the corotation frame or the inertial frame
    """
    ProgradeNegative = True
    def __init__(self, val=0., unit=None, *, err=0., norm=None,
                 l=None, m=None, k=None, n=None,
                 rot=0, corot=False, folded: bool=None,
                 extra: dict=None
                 ):
        if isinstance(val, Mode):
            self.val=val.val
            self.err=val.err
            self.unit=val.unit
            self.norm=val.norm
            self.n = val.n
            self.m = val.m
            self.l = val.l
            self.k = val.k
            self.rot = val.rot
            self.corot = val.corot
            self.folding_status = val.folding_status
            self.extra = val.extra
            return
        else:
            super().__init__(val, unit, err=err, norm=norm, extra=extra)

        self.rot = Freq(rot)
        self.corot = corot
        if folded is None:
            self.folding_status = 0
        else:
            self.folding_status = -2 if folded else 2
        self.n = n
        self.m = m
        self.l = l
        self.k = k
        if l is not None and k is None and m is not None:
            self.k = l-abs(m)
        if k is not None and l is None and m is not None:
            self.l = abs(m)+k

    def set_rot(self, rot, folded=None):
        """
        set a (new) rotation. It must be done in the inertial frame.
        Its purpose is to set a (possible) rotation to an observational series of frequency/mode
        By changing the rotation in a model we must also change the values of the frequency in corot.
        """
        rot=Freq(rot)
        if(self.corot):
            print('set_rot is allowed only in the inertial frame')
        else:
            self.rot=rot
            if abs(self.folding_status)<2: #if not forced by the user reset it status
                self.folding_status = 0
            if folded is not None:
                self.folding_status = -2 if folded else 2

    def set_mlk(self, m=None, *, l=None, k=None):
        """
        set a (new) identification. It must be done in the inertial frame.
        """
        if m is not None:
            self.m=m
        if l is not None:
            self.l=l
            if self.m is not None:
                self.k = l-abs(self.m)
        if  k is not None:
            self.k = k
            if self.m is not None:
                self.l = abs(self.m)+k


    @staticmethod
    def frame_change(mode, frame_new, folding=False):
        if(mode.corot):
            frame_old='co'
        else:
            frame_old='in'
        if(frame_new[:2] == frame_old): return mode.copy()
        if mode.m is None: return mode.copy() #no change possible
        if (mode.ProgradeNegative):
            m = mode.m
        else:
            m = -mode.m
        new=Freq.frame_change(mode, frame_old, frame_new, mode.rot, m, folding)
        new.corot = (frame_new[:2] == 'co')
        if(new.corot):
            new.folding_status = 0
            if new.val < 0:
                pass
                #print("rotation is too large compared to frequency")
        else: #inertial frame
            if new.val < 0:
                new.val = abs(new.val)
                new.folding_status = -1 #this frequency has been fold.
            else:
                new.folding_status = 1 #this frequency has not been fold
        return new

    def to_frame(self, frame, folding=None):
        if(frame[:2] != 'co') and (frame[:2] != 'in'):
            print('unknown frame')
            raise ValueError

        if folding is None:
            if self.folding_status < 0:
                folding=True
            elif self.folding_status > 0:
                folding=False
            else:
                if self.k is not None:
                    folding = self.k < -1 #folding for Rossby modes
                else:
                    folding = False
        self.update(Mode.frame_change(self,frame,folding))

    def getve(self, unit=None, frame=None, folding=None, norm=None):
        """
        get the value of the frequency and the associated error.
        If unit is specified, the values are converted in the requested unit
        """
        if frame is not None:
            self=self.copy()
            self.to_frame(frame, folding)

        return super().getve(unit, norm)


    def getv(self, unit=None, frame=None, folding=None):
        """
        get the value of the frequency.
        If unit is specified, the values are converted in the requested unit
        """
        val,_=self.getve(unit, frame, folding)
        return val

    def gete(self, unit=None, frame=None, folding=None):
        """
        get the value of the associated error.
        If unit is specified, the values are converted in the requested unit
        """
        _,err=self.getve(unit, frame, folding)
        return err

    def gets(self):
        if(not self.corot):
            self = self.copy()
            self.to_frame('co')
        nu = self.getv('µHz')
        rot= self.rot.getv('µHz')
        return 2*rot/nu


    def __str__(self):
        if self.n is None:
            n=''
        else:
            n=self.n
        if self.l is None:
            l=''
        else:
            l=self.l
        if self.m is None:
            m=''
        else:
            m=self.m
        if self.err == 0.:
            err=''
        else:
            err=f' +- {self.err}'

        cor=''
        if self.corot: cor=' (corot)'
        str=Freq.__str__(self)
        return f'({n},{l},{m}) '+str+cor

    def __repr__(self):
        return 'Mode: '+str(self)

class ModeSet:
    def __init__(self, val=None, /, unit=None, *, err=0., norm=None,
                 l=None, m=None, k=None, n=None,
                 rot=0, corot=False,
                 extra=None):

        self.mode_list=[]
        if val is None: #empty set
            return

        if isinstance(val, ModeSet):
            self.mode_list = val.mode_list #it is not a copy ; to ensure get_item have the expected behaviour
            return
        elif isinstance(val, Mode):
                self.mode_list =[val]
                return
        elif isinstance(val, (tuple, list, _np.ndarray)):
            if all([isinstance(m, Mode) for m in val]):
                self.mode_list = list(val)
                return
            if all([isinstance(m, ModeSet) for m in val]):
                for i in range(0,len(val)):
                    self.append(val[i])
                return

        val_a = _np.array([val]).flatten()
        unit_a = _np.array([unit]).flatten()
        err_a = _np.array([err]).flatten()
        norm_a = _np.array([norm]).flatten()
        l_a  = _np.array([l]).flatten()
        m_a  = _np.array([m]).flatten()
        k_a  = _np.array([k]).flatten()
        n_a  = _np.array([n]).flatten()
        rot_a  = _np.array([rot]).flatten()
        corot_a  = _np.array([corot]).flatten()
        extra_a  = _np.array([extra]).flatten()


        for i,v in enumerate(val_a):
            iu=0 if(unit_a.size == 1) else i
            ie=0 if(err_a.size == 1) else i
            i_no=0 if(norm_a.size == 1) else i
            il=0 if(l_a.size == 1) else i
            ik=0 if(k_a.size == 1) else i
            im=0 if(m_a.size == 1) else i
            i_n=0 if(n_a.size == 1) else i
            ir=0 if(rot_a.size == 1) else i
            ic=0 if(corot_a.size == 1) else i
            ix=0 if(extra_a.size == 1) else i
            self.mode_list.append(Mode(v, unit_a[iu], err=err_a[ie], norm=norm_a[i_no],
                                       l=l_a[il], m=m_a[im],
                                       k=k_a[ik], n=n_a[i_n],
                                       rot=rot_a[ir], corot=corot_a[ic],
                                       extra=extra_a[ix]))

    def __getitem__(self, index):
        res = _np.array(self.mode_list)[index]
        if isinstance(res, Mode):
            return res
        else:
            return ModeSet(res)

    def append(self,mode):
        if isinstance(mode, (ModeSet, list, tuple, _np.ndarray)):
            for i in range(len(mode)):
                self.mode_list.append(Mode(mode[i]))
        else:
            self.mode_list.append(Mode(mode))


    def getve(self, unit=None, frame=None, folding=None):
        """
        get the value of the frequency and the associated error.
        If unit is specified, the values are converted in the requested unit
        """
        val_list = []
        err_list = []
        for m in self.mode_list:
            val,err = m.getve(unit, frame, folding)
            val_list.append(val)
            err_list.append(err)

        return _np.array(val_list),_np.array(err_list)

    def getv(self, unit=None, frame=None, folding=None):
        """
        get the value of the frequency.
        If unit is specified, the values are converted in the requested unit
        """
        val,_=self.getve(unit, frame, folding)
        return val

    def gete(self, unit=None, frame=None, folding=None):
        """
        get the value of the frequency error.
        If unit is specified, the values are converted in the requested unit
        """
        _,err=self.getve(unit, frame, folding)
        return err

    def gets(self):
        """
        get the value of the spin parameter
        """
        s_list=[]
        for m in self.mode_list:
            s_list.append(m.gets())

        return _np.array(s_list)


    def to(self, unit):
        """
        change the unit of the values and the associated errors
        """
        for m in self.mode_list:
            m.to(unit)

    def to_frame(self, frame, folding=None):
        """
        change the frame (inertial or corotating)
        """
        for m in self.mode_list:
            m.to_frame(frame, folding)

    def set_err(self, err):
        """
        reset the same error for all Modes of the set
        """
        for m in self.mode_list:
            m.set_err(err)

    def set_rot(self, rot):
        """
        reset the same rotation for all Modes of the set
        """
        for m in self.mode_list:
            m.set_rot(rot)

    def set_mlk(self, m=None, *, l=None, k=None):
        """
        reset the same identification for all Modes of the set
        """
        for mode in self.mode_list:
            mode.set_mlk(m,l=l,k=k)

    def __len__(self):
        return len(self.mode_list)

    def set_extra(self,key,val):
        val=_np.array(val).flatten().squeeze()
        if val.ndim == 0:
            for mode in self.mode_list:
                mode.set_extra(key,val)
        else:
            if(len(self) != val.size):
                raise ValueError('val has to the correct number of elements')
            for im,mode in enumerate(self.mode_list):
                mode.set_extra(key,val[im])


    def get(self, key):
        var_list=[]
        for m in self.mode_list:
            var_list.append(m.get(key))

        return _np.array(var_list)


    def __str__(self):
        #return str(self.mode_list)
        if len(self)==0: return '[]'
        out_str='['
        for i,mode in enumerate(self.mode_list):
            stri='' if i==0 else ' '
            strf=']' if i==len(self)-1 else ',\n'
            out_str=out_str+stri+str(mode)+strf
        return out_str

    def __repr__(self):
        if len(self)<9:
            return 'ModeSet('+str(self)+')'
        else:
            out_str='ModeSet(['
            for i in range(3):
                out_str=out_str+str(self.mode_list[i])+',\n'
            out_str=out_str+'   \u22EE\n'
            for i in range(-3,0):
                strf='])' if i==-1 else ',\n'
                out_str=out_str+str(self.mode_list[i])+strf
            return out_str


    def copy(self):
        return _copy.deepcopy(self)