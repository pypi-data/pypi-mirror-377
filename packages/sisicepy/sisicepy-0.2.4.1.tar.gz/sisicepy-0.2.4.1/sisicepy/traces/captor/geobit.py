import xarray as xr
import numpy as np
import pint_xarray
from pint_xarray import unit_registry as ureg


def C100_ZPK():
    '''
    Value for Poles and Zeros function of the Geobit C100

    Zeros: [0+0i,0+0i]
    Poles :[-15.8336-23.4251i,-15.8336+23.4251i]
    K = 28.8 V/(m.s^-1)
    '''

    Zs=[0+0j,0+0j]
    Ps=[np.complex128(-15.8336-23.4251j),np.complex128(-15.8336+23.4251j)]
    K = 28.8*ureg.volt*ureg.second/ureg.meter

    return Zs,Ps,K

def S100_ZPK():
    '''
    Value for Poles and Zeros function of the Geobit S100

    Zeros: [0+0i,0+0i,0+0i]
    Poles :[-615+0i,-0.406-0.606i,-0.406+0.606i,-1.226313+0j]
    K = 1500*616 V/(m.s^-1)
    '''

    Zs=[0+0j,0+0j,0+0j]
    Ps=[np.complex128(-615+0j),np.complex128(-0.406-0.606j),np.complex128(-0.406+0.606j),np.complex128(-1.226313+0j)]
    K = 1500*616*ureg.volt*ureg.second/ureg.meter

    return Zs,Ps,K