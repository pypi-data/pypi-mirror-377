import xarray as xr
import numpy as np
import pint_xarray
from pint import Quantity
from pint_xarray import unit_registry as ureg
import scipy.signal


def PSD(self,**kwargs):
    '''
    Wrapper of `scipy.signal.welch` function for Power Spectral Density.
    :param self:
    :type self: xr.DataArray
    '''

    # sampling frequency
    fs=1/(np.float64((self._obj.time[1]-self._obj.time[0]))*10**-9)

    freq,psd=scipy.signal.welch(self._obj,fs=fs,**kwargs)
    
    da_psd=xr.DataArray(psd,dims='freq')*(self._obj.pint.units)**2/ureg.hertz
    da_psd['freq']=freq

    return da_psd

def spectrogram(self,win,t_start,dB=True,**kwargs):
    '''
     Wrapper of `scipy.signal.welch` to performed PSD spectrogram
    :param self:
    :type self: xr.DataArray
    :param win: time length in seconds
    :type win: int
    :param t_start: data for the start
    :type t_start: str
    :param dB: value in dB
    :type dB: bool
    '''
    da=self._obj
    fs=1/(np.float64((self._obj.time[1]-self._obj.time[0]))*10**-9)

    # Sub data selection
    da_sel=da.sel(time=slice(t_start,None))
    # Find the number of win interval in the time serie
    nb_per=int(len(da_sel)/(win*fs))
    # select the right time length for the spectrogram
    da_sel=da_sel[0:np.int32(win*fs*nb_per)]

    freq,psd=scipy.signal.welch(da_sel.values.reshape(nb_per,int(win*fs)),fs,**kwargs)
    # Covert in dB
    if dB:
        psd=10*np.log10(psd)
        unit_dB=ureg.dB
    else:
        unit_dB=1.

    da_psd=xr.DataArray(np.transpose(psd),dims=['freq','time'])*(self._obj.pint.units)**2/ureg.hertz
    da_psd['freq']=freq

    tr_time=da_sel.time.values.reshape(nb_per,int(win*fs))
    da_psd['time']=tr_time[:,0]

    return da_psd

#----------------------------------------------------------------------------------------------
xr.DataArray.traces.PSD = PSD
xr.DataArray.traces.spectrogram = spectrogram