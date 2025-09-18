from .Freq import Freq
import numpy as _np
import matplotlib.pyplot as _plt
from .basic import smooth, rebin

class PSD:

    def __init__(self, x, y, xunit='µHz', yunit='ppm2/µHz', extra={}):

        if isinstance(xunit, Freq):
            self.xunit = xunit
        else:
            self.xunit = Freq(1,xunit)

        self.yunit = yunit
        self.x = _np.array(x).flatten()
        self.y = _np.array(y).flatten()
        self.extra = extra
        self.size = x.size
        if(self.size != y.size):
            raise ValueError(f'x and y must have the same size {self.x.size}, {self.y.size}')

    def to_xunit(self, xunit_new):

        if not isinstance(xunit_new, Freq):
            xunit_new = Freq(1,xunit_new)

        for i in range(len(self.x)):
            xfreq = Freq(self.x[i]*self.xunit.val,self.xunit.unit)
            self.x[i]=xfreq.getv(xunit_new.unit)/xunit_new.val
        self.xunit = xunit_new


    def __getitem__(self, index):
            return PSD(self.x[index], self.y[index], self.xunit, self.yunit, self.extra)

    def __len__(self):
        return self.size

    def __repr__(self):
        res=f'PSD( size: {self.size}, xunit: {self.xunit}, yunit: {self.yunit}\n'
        res+='x: '+repr(self.x)+'\n'
        res+='y: '+repr(self.y)+')'
        return res

    def plot(self,ax=None, *, smooth_window=1, bin=1, **kwargs_plot):
        if ax is None:
            _,ax=_plt.subplots()

        x=self.x ; y=self.y
        if bin>1:
            x=rebin(x,bin)
            y=rebin(y,bin)
        if smooth_window>1:
            y=smooth(y, smooth_window)

        ax.plot(x,y, **kwargs_plot)

        ax.set_ylabel(f'Spectrum ({self.yunit})')
        if self.xunit.val == 1:
            xunit_str=self.xunit.unit
        else:
            xunit_str=str(self.xunit)
        if self.xunit.unit in Freq.unit_f_list:
            xtype='frequency'
        else:
            xtype='period'

        ax.set_xlabel(f'{xtype} ({xunit_str})')

        try:
            title=self.extra['OBJECT']
            ax.set_title(title)
        except:
            pass


class LightCurve:

    def __init__(self, x, y, xunit='d', yunit='ppm', extra={}):

        if isinstance(xunit, Freq):
            self.xunit = xunit
        else:
            self.xunit = Freq(1,xunit)
        if self.xunit.unit not in Freq.unit_P_list:
            raise ValueError(f'xunit must be a time unit (s,d...), not {self.xunit.unit}')

        self.yunit = yunit
        self.x = _np.array(x).flatten()
        self.y = _np.array(y).flatten()
        self.extra = extra
        self.size = x.size
        if(self.size != y.size):
            raise ValueError(f'x and y must have the same size {self.x.size}, {self.y.size}')

    def to_xunit(self, xunit_new):

        if not isinstance(xunit_new, Freq):
            xunit_new = Freq(1,xunit_new)
        if xunit_new.unit not in Freq.unit_P_list:
            raise ValueError(f'xunit must be a time unit (s,d...), not {xunit_new.unit}')

        for i in range(len(self.x)):
            time_new = Freq(self.x[i]*self.xunit.val,self.xunit.unit)
            self.x[i]=time_new.getv(xunit_new.unit)/xunit_new.val
        self.xunit = xunit_new


    def __getitem__(self, index):
            return LightCurve(self.x[index], self.y[index], self.xunit, self.yunit, self.extra)

    def __len__(self):
        return self.size

    def __repr__(self):
        res=f'LightCurve( size: {self.size}, xunit: {self.xunit}, yunit: {self.yunit}\n'
        res+='x: '+repr(self.x)+'\n'
        res+='y: '+repr(self.y)+')'
        return res

    def plot(self,ax=None, *, smooth_window=1, bin=1, **kwargs_plot):
        if ax is None:
            _,ax=_plt.subplots()

        x=self.x ; y=self.y
        if bin>1:
            x=rebin(x,bin)
            y=rebin(y,bin)
        if smooth_window>1:
            y=smooth(y, smooth_window)

        ax.plot(x,y, **kwargs_plot)

        ax.set_ylabel(f'LC ({self.yunit})')
        if self.xunit.val == 1:
            xunit_str=self.xunit.unit
        else:
            xunit_str=str(self.xunit)

        ax.set_xlabel(f'time ({xunit_str})')

        try:
            title=self.extra['OBJECT']
            ax.set_title(title)
        except:
            pass
