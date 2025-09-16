import xarray as xr
import pyrocko.io
import numpy as np
from datetime import datetime, timezone, timedelta
import pandas as pd
import pint_xarray
import natsort
import glob
from pint_xarray import unit_registry as ureg

def load_datacube(adr,comp=[0],force_freq=None):
    '''
    Loader for DIGOS DataCube

    :param adr: Path to the DataCube file
    :type adr: str
    :param comp: List of componant to load
    :type comp: list of int
    :return: xarray Dataset containing the loaded data and metadata
    :rtype: xarray.Dataset
    '''

    data=pyrocko.io.load(adr,format='datacube')


    df=xr.Dataset()
    
    for i in comp:
        df['comp_'+str(i)]=xr.DataArray(data[i].ydata,dims='time')*ureg.bit
        for name in data[0].meta:
            df['comp_'+str(i)].attrs[name]=data[0].meta[name]
            df['comp_'+str(i)].attrs[name]=data[0].meta[name]
        
    ti=datetime.fromtimestamp(data[0].tmin,tz=timezone.utc)
    tf=datetime.fromtimestamp(data[0].tmax,tz=timezone.utc)
    df['time']=pd.date_range(ti,tf,data[0].data_len()).values
    
    
    for name in data[0].meta:
        df.attrs[name]=data[0].meta[name]
        df.attrs[name]=data[0].meta[name]

    if force_freq is not None:
        if force_freq!=np.int32(df.attrs['S_RATE']):
            print('Resample signal !')
            f=str(1/force_freq)+'s'
            df=df.resample(time=f).nearest('1ns')
            df.attrs['S_RATE']=str(force_freq)

    return df

def load_mfdatacube(adr_list,cor=False ,**kwargs):
    '''
    Loader for DIGOS DataCube

    :param adr_list:
    :type adr_list: list
    '''

    data_list=[]
    for adr in adr_list:
        data_list.append(load_datacube(adr,**kwargs))

    data=xr.concat(data_list,dim='time')

    if len(np.diff(data.time.values))>2 and cor:
        print('Delete duplicate !')
        data = data.sel(time=~data.get_index('time').duplicated())
        df = data.interpolate_na(dim='time')*ureg.bit
        for key in list(data.keys()):
            df[key].attrs.update(data.attrs)
    else:
        df=data
        
    return df


def open_day_datacube(path,day,**kwargs):
    '''
    Loader for DIGOS DataCube for a given day

    :param day: format %Y-%m-%d
    :type day: str
    '''
    files=natsort.natsorted(glob.glob(path))
    # function to parse the path from datacube to string date
    def extract_date(file):
        yr_folder=int(file.split('/')[-2][0:2])
        day_folder=int(file.split('/')[-2][2:6])
        day_files=int(file.split('/')[-1][0:4])
        if day_files<day_folder:
            date='20'+str(yr_folder+1)+str(day_files).zfill(4)
        else:
            date='20'+str(yr_folder)+str(day_files).zfill(4)
        return date

    formatted_dates = list(map(extract_date, files))

    ###########################################################
    # find file for the given day and one day before and afer #
    ###########################################################
    formatted_dates_dt = np.array([datetime.strptime(date, '%Y%m%d') for date in formatted_dates])

    # Define the target date (D-Day)
    target_date = datetime.strptime(day, '%Y%m%d')

    # Define the previous day and next day
    previous_day = target_date - timedelta(days=1)
    next_day = target_date + timedelta(days=1)

    # Use np.where to find indices for the target date, previous day, and next day
    indices = np.where(
        (formatted_dates_dt == target_date) |
        (formatted_dates_dt == previous_day) |
        (formatted_dates_dt == next_day)
    )

    #############
    # Open data #
    #############
    if len(indices[0]) != 0:
        di=day+'T00:00:00'
        df=next_day.strftime('%Y%m%d')+'T00:00:00'
        return load_mfdatacube(np.array(files)[indices[0]],**kwargs).sortby("time").sel(time=slice(di,df))
    else:
        print('No data at this date !')

