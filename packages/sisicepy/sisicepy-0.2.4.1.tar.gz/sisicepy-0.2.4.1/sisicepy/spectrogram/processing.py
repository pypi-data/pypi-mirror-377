import xarray as xr
from pint_xarray import unit_registry as ureg

def to_energy(self,low_freq,high_freq):
    '''
    Compute the energy between the given range of frequencies

    :param low_freq:
    :type low_freq: float
    :param high_freq:
    :type high_freq: float
    '''

    return self._obj.sel(freq=slice(low_freq,high_freq)).integrate('freq')*ureg*hertz

# --------------------------------------------
xr.DataArray.spectrogram.to_energy = to_energy