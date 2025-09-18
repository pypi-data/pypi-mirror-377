from ..Freq import Freq

__all__=['ModelAsympRG']

class ModelAsympRG:

    def __init__(self,
                 numax, Dnu, eps_p, a_2, d01,
                 Pi1, eps_g,
                 q,
                 rot_g=0., rot_p=0.,
                 nu_mag=0., a_mag=0.,
                 *, component=(True, True, True), nu_unit='µHz', P_unit='s'):


        self.numax=Freq(numax,nu_unit)
        self.Dnu=Freq(Dnu,nu_unit)
        self.eps_p=eps_p
        self.a_2=a_2
        self.d01=Freq(d01,nu_unit)

        self.Pi1=Pi1=Freq(Pi1,P_unit)
        self.eps_g=eps_g

        self.q=q

        self.rot_g=Freq(rot_g,nu_unit)
        self.rot_p=Freq(rot_p,nu_unit)

        self.nu_mag=Freq(nu_mag,nu_unit)
        self.a_mag = a_mag

        self.p_param = (self.numax, self.Dnu, self.eps_p, self.a_2, self.d01)
        self.g_param = (self.Pi1, self.eps_g)
        self.rot_param=(self.rot_g,self.rot_p)
        self.mag_param=(self.nu_mag, self.a_mag)
        self.component=component

    def update(self, *,
                 numax=None, Dnu=None, eps_p=None, a_2=None, d01=None,
                 Pi1=None, eps_g=None,
                 q=None,
                 rot_g=None, rot_p=None,
                 nu_mag=None, a_mag=None,
                 component=None, nu_unit='µHz', P_unit='s'):

        if numax is not None: self.numax=Freq(numax, nu_unit)
        if Dnu is not None: self.Dnu=Freq(Dnu, nu_unit)
        if eps_p is not None: self.eps_p=eps_p
        if a_2 is not None: self.a_2=a_2
        if d01 is not None: self.d01=Freq(d01, nu_unit)
        if Pi1 is not None: self.Pi1=Freq(Pi1, P_unit)
        if eps_g is not None: self.eps_g=eps_g
        if q is not None: self.q=q
        if rot_g is not None: self.rot_g=Freq(rot_g, nu_unit)
        if rot_p is not None: self.rot_p=Freq(rot_p, nu_unit)
        if nu_mag is not None: self.nu_mag=Freq(nu_mag, nu_unit)
        if a_mag is not None: self.a_mag=a_mag
        if component is not None: self.component=component

        self.p_param = (self.numax, self.Dnu, self.eps_p, self.a_2, self.d01)
        self.g_param = (self.Pi1, self.eps_g)
        self.rot_param=(self.rot_g,self.rot_p)
        self.mag_param=(self.nu_mag, self.a_mag)

    def __str__(self):
        str=f'numax={self.numax}, Dnu={self.Dnu}, eps_p={self.eps_p:.2f}, '
        str+=f'a_2={self.a_2}, d01={self.d01}\n'
        str+=f'Pi1={self.Pi1}, eps_g={self.eps_g:.2f}, q={self.q:.3f}\n'
        str+=f'rot_g={self.rot_g}, rot_p={self.rot_p}\n'
        str+=f'nu_mag={self.nu_mag}, a_mag={self.a_mag:.2f}'
        return str

    def __repr__(self):
        return 'ModelAsympRG(\n'+str(self)+' )'

