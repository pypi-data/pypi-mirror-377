import numpy as np
from seispack import Freq, ModeSet, Mode
from seispack import generate_aTAR, plot_stretch_rot

# create a model
rot=Freq(0.5,'d') #rotation 0.5d
Pi0=Freq(3900,'s') #Pi0 3900s
eps=0.45

set1=generate_aTAR(Pi0,rot,eps,n=(55,95),m=-1,l=1) #generate l=1 Kelvin modes
set1.to_frame('in') #into inertial frame
nu=set1.getv('muHz') # frequency list in µHz
nmode=nu.size

err=Freq(3,'nHz') #define an error af 3 nHz

# generate errors of frequencies and random amplitude between 0 and 10.
np.random.seed(9876543)
amplitude=np.random.uniform(0.,10.,nmode)
noise=np.random.normal(size=nmode)
nuobs=nu+noise*err.getv('µHz')

index_select=amplitude>2.0
nuobs_ok=nuobs[index_select]
amplitude_ok=amplitude[index_select]

# generate observation set
obs_set=ModeSet(nuobs_ok,'µHz',err=err) # by default in inertial frame, ok

#add information on amplitude in the extra parameters
obs_set.set_extra('amp',amplitude_ok)

# plot the streched echelle diagram
plot_stretch_rot(obs_set, Pi0, rot, m=-1, l=1, yunit='µHz', model=set1, outputfile='sed_fake_gdor.pdf')
