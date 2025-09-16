import xarray as xr
import pyrocko.io
import numpy as np
from datetime import datetime, timezone
import pandas as pd
import pint_xarray
from pint_xarray import unit_registry as ureg

def load_mseed(adr,gain=16):
    '''
    Loader for DIGOS DataCube

    :param axis: list of the axis to load
    :type axis: list
    '''

    data=pyrocko.io.load(adr,format='mseed')[0]

    da=xr.DataArray(data.ydata,dims='time')*ureg.bit
        
    ti=datetime.fromtimestamp(data.tmin,tz=timezone.utc)
    tf=datetime.fromtimestamp(data.tmax,tz=timezone.utc)
    da['time']=pd.date_range(ti,tf,data.data_len()).values

    da.attrs['P_AMPL']=gain
    
    return da