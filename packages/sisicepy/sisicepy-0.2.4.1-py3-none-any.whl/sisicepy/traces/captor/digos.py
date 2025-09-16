import xarray as xr
import numpy as np
import pint_xarray
from pint_xarray import unit_registry as ureg

def geophone_ZPK():
    '''
    Value for Poles and Zeros function of the Digos Geophone

    Zeros: [0,0]
    Poles :[-19.78+20.20i,-19.78-20.20i]
    K=27.7 V/(m.s^-1)
    '''

    Zs=[0,0]
    Ps=[np.complex128(-19.78+20.20j),np.complex128(-19.78-20.20j)]
    K = 27.7*ureg.volt*ureg.second/ureg.meter

    return Zs,Ps,K