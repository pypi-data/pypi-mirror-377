import xarray as xr
import numpy as np
import pint_xarray
from pint_xarray import unit_registry as ureg

def count2volt_datacube(self,Vpp=4.096,nb_bin=2**24):
    '''
    Convert numeric value to Voltage for DataCube

    :param Vpp: peak to peak value, default: 4.096 (unit V)
    :type Vpp: float
    :param nb_bin: number of integer for the numerisation, default: 2**24
    :type nb_bin: int
    '''

    coeff   =  Vpp/nb_bin/np.int32(self._obj.attrs['P_AMPL']) * ureg.volt/ureg.bit
    
    return self._obj*coeff

def bob_S100(self):
    '''
    Apply Digos BreakOutBox for S100 the divide by 4 the response
    '''

    return self._obj*4

#-----------------------------------------------------------------------------
xr.DataArray.traces.count2volt_datacube = count2volt_datacube
xr.DataArray.traces.bob_S100 = bob_S100