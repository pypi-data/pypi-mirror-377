import xarray as xr
import numpy as np
import pint_xarray
from pint import Quantity
from pint_xarray import unit_registry as ureg

def trapezoid(self,band,delta):
    '''
    Trapeziod band filter:
    .. line-block::  
        ........Lower band...........Higher band........
        ........band[0]...............band[1]...........
        ...........|------------------|.................
        ..........||..................||................
        .........|||..................|||...............
        ........||||..................||||..............
        .......|||||..................|||||.............
        ......||||||..................||||||............
        _____|||||||..................|||||||_______....
        .......delta..................delta.............


    :param self: signal to filter with trapeziode band
    :type self: xr.DataArray
    :param band: lower band and higher band ex: [4.5,90] Hz
    :type band: list
    :param delta: delta for the begining and the end of the trapez
    :type delta: float
    '''

    da=self._obj

    # delta t 
    dt=np.int32(da.time[1]-da.time[0])*10**-9 # because time unit is ns

    # compute FFT of da
    da_FFT=np.fft.fftshift(np.fft.fft(da))
    # and associated frequencies
    da_freq=np.fft.fftshift(np.fft.fftfreq(len(da),d=dt))
    
    ######################
    ## Construct trapez ##
    ######################
    # trap_side is a function to extract value for the linear part
    # between 0 and 1 sign=+1 and 1 and 0 sign=0
    def trap_side_pos(x,delta,Pup,sign=1):
        return sign*1/delta*x+1-sign*Pup/delta
    
    def trap_side_neg(x,delta,Pup,sign=1):
        return sign*1/delta*x+1+sign*Pup/delta
    
    # Build trapez for >0 frequencies in the spectrum
    # Build 0 1 array with 1 value in the band interval
    Top_Trap_U=(da_freq>band[0])*(da_freq<band[1])
    # Build line part 0 to 1 
    Up_Trap_U=(da_freq>=band[0]-delta)*(da_freq<=band[0])
    Up_Trap_U=trap_side_pos(da_freq,delta,band[0],sign=1)*Up_Trap_U
    # Build line part 1 to 0
    Dw_Trap_U=(da_freq>=band[1])*(da_freq<=band[1]+delta)
    Dw_Trap_U=trap_side_pos(da_freq,delta,band[1],sign=-1)*Dw_Trap_U

    # Build trapez for >0 frequencies in the spectrum
    # Build 0 1 array with 1 value in the band interval
    Top_Trap_B=(da_freq<-1*band[0])*(da_freq>-1*band[1])
    # Build line part 0 to 1 
    Up_Trap_B=(da_freq>=-1*band[1]-delta)*(da_freq<=-1*band[1])
    Up_Trap_B=trap_side_neg(da_freq,delta,band[1],sign=1)*Up_Trap_B
    # Build line part 1 to 0
    Dw_Trap_B=(da_freq>=-1*band[0])*(da_freq<=-1*band[0]+delta)
    Dw_Trap_B=trap_side_neg(da_freq,delta,band[0],sign=-1)*Dw_Trap_B


    # compute full trapez
    all_trap=Top_Trap_U+Up_Trap_U+Dw_Trap_U+Top_Trap_B+Up_Trap_B+Dw_Trap_B
    trapez=xr.DataArray(all_trap,dims=['freq'])
    trapez['freq']=da_freq
    
    ###############################
    ## Apply full trapez to data ##
    ###############################
    # Apply only on the real part
    FFT_filtered=da_FFT*trapez*ureg.second*da.pint.units

    # Compute filtered signal
    signal_filtered=xr.DataArray(np.fft.ifft(np.fft.ifftshift(FFT_filtered)),dims=da.dims)*da.pint.units
    for name in da.dims:
        signal_filtered[name]=da[name]

    return signal_filtered.real,FFT_filtered,trapez


def poles_zeros_filter(self,ZPG,waterlevel):
    '''
    Pole and zeros filter
    (https://en.wikipedia.org/wiki/Pole%E2%80%93zero_plot)

    :param self: signal to filter
    :type self: xr.DataArray
    :param ZPG: [zeros,poles,gains]
    :type ZPG: list
    :param waterlevel:
    :type waterlevel: float
    '''
    
    da=self._obj

    # delta t 
    dt=np.int32(da.time[1]-da.time[0])*10**-9 # because time unit is ns

    # compute FFT of da
    da_FFT=np.fft.fftshift(np.fft.fft(da))
    # and associated frequencies
    da_freq=np.fft.fftshift(np.fft.fftfreq(len(da),d=dt))

    ####################################
    ## Construct poles_zeros_function ##
    ####################################
    def poles_zeros(zeros,poles,gains,freq,waterlevel):
        N=1
        for Zi in zeros:
            N = N*(2*np.pi*1j*freq - Zi)

        D = 1
        for Pi in poles:
            D = D*(2*np.pi*1j*freq - Pi)
        
        transfer=gains*N/D
        # waterlevel
        temp1=transfer*np.conj(transfer)
        gamma=np.max(temp1)*waterlevel
        filter_np=np.conj(transfer)/(temp1+gamma)
        filter=xr.DataArray(filter_np,dims='freq')
        filter['freq']=freq

        
        return filter
    
    filter_poles_zeros=poles_zeros(ZPG[0],ZPG[1],ZPG[2],da_freq,waterlevel)
    ###############################
    ## Apply full trapez to data ##
    ###############################
    # Apply only on the real part
    FFT_filtered=da_FFT*filter_poles_zeros*ureg.second*da.pint.units

    # Compute filtered signal
    signal_filtered=xr.DataArray(np.fft.ifft(np.fft.ifftshift(FFT_filtered)),dims=da.dims)*FFT_filtered.pint.units/ureg.second
    
    for name in da.dims:
        signal_filtered[name]=da[name]
     
    return signal_filtered.real,FFT_filtered,filter_poles_zeros

#----------------------------------------------------------------------------------------------
xr.DataArray.traces.trapezoid = trapezoid
xr.DataArray.traces.poles_zeros_filter = poles_zeros_filter
