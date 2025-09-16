import xarray as xr

@xr.register_dataarray_accessor("traces")

class traces(object):
    '''
    This is a classe to work on seismic traces using xarray.
    '''
    
    def __init__(self, xarray_obj):
        '''
        Constructor for traces. 
        
        :param xarray_obj:
        :type xarray_obj: xr.DataArray
        '''
        self._obj = xarray_obj 
    pass

from sisicepy.traces.io import datacube_loader
from sisicepy.traces.recorder import datacube
from sisicepy.traces.signal import freq_filter
from sisicepy.traces.signal import utils
from sisicepy.traces.signal import processing
from sisicepy.traces.captor import geobit
from sisicepy.traces.captor import digos
