import xarray as xr
import scipy.signal
import pint_xarray
from pint_xarray import unit_registry as ureg

def remove_mean(self):
    '''
    Remove mean from da signal

    :param self: signal
    :type self: xr.DataArray
    '''
    
    return self._obj-self._obj.mean()

def remove_trend(self):
    '''
    Remove linear trend from da signal

    :param self: signal
    :type self: xr.DataArray
    '''

    da=self._obj

    da_no_trend=xr.DataArray(scipy.signal.detrend(da),dims=da.dims)
    for name in da.dims:
        da_no_trend[name]=da[name]

    return da_no_trend*da.pint.units

#---------------------------------------------------------------------------
xr.DataArray.traces.remove_mean = remove_mean
xr.DataArray.traces.remove_trend = remove_trend