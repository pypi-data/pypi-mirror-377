import xarray as xr

@xr.register_dataarray_accessor("spectrogram")

class spectrogram(object):
    '''
    This is a classe to work on seismic spectrogram using xarray.
    '''
    
    def __init__(self, xarray_obj):
        '''
        Constructor for traces. 
        
        :param xarray_obj:
        :type xarray_obj: xr.DataArray
        '''
        self._obj = xarray_obj 
    pass

from sisicepy.spectrogram import processing