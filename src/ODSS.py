#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 20:45:25 2018

@author: jdlara
"""

import opendssdirect as dss
import pandas as pd
from opendssdirect.utils import Iterator
import os

def loadDSS():
    current_directory = os.path.realpath(os.path.dirname(__file__))
    master_file = os.path.join(current_directory,'../data/DSS_files/master.dss')
    dss.Basic.DataPath(current_directory)
    dss.run_command("clear")
    dss.run_command('compile {master}'.format(master=master_file))
    
    return dss


def DSSrunsnap(dss, show = False):
    dss.run_command('set mode=snap')
    dss.run_command('Solve')

    if show == True:
        dss.run_command('show Powers kva Elements')

    return dss

def DSSrunts(dss, run_type):
    dss.run_command('set mode={0}'.format(run_type))
    dss.run_command('set stepsize=1h')
    dss.run_command('Solve')
    
    return dss

def addMonitors(dss):
    for load in dss.Loads.AllNames():
        dss_command_v = 'New monitor.{0}_voltage element=Load.{0} term=1 mode=32 Ppolar=no'.format(load)
        dss.run_command(dss_command_v)
        dss_command_p = 'New monitor.{0}_power element=Load.{0} term=1 mode=33 Ppolar=no'.format(load)
        dss.run_command(dss_command_p)
    
    for sources in dss.Vsources.AllNames():
        dss_command_v = 'New monitor.{0}_voltage element=Vsource.{0} term=1  mode=32 Ppolar=no'.format(sources)
        dss.run_command(dss_command_v)
        dss_command_p = 'New monitor.{0}_power element=Vsource.{0} term=1 mode=33 Ppolar=no'.format(sources)
        dss.run_command(dss_command_p)
    
    return dss 

def addLoadTimeSeries(dss, run_type, filename):
    #Read Time Series CSV file
    current_directory = os.path.realpath(os.path.dirname(__file__))
    load_file = os.path.join(current_directory,'../data/time_series/{0}'.format(filename))
    results = []
    with open(load_file) as csvfile:
        results = [float(s) for line in csvfile.readlines() for s in line[:-1].split(',')]
    
    #create new load shape
    dss.LoadShape.New('load')
    #dss.LoadShape.Name('load')
    dss.LoadShape.HrInterval(1)
    dss.LoadShape.Npts(len(results))
    dss.LoadShape.PMult(results)
    
    #assign the load shape to all loads
    for l in Iterator(dss.Loads,run_type):
        if (l()==run_type):
            continue
        l('load')
    
    return dss
 
def addSolarTimeSeries(dss,filename):
    #Read Time Series CSV file
    current_directory = os.path.realpath(os.path.dirname(__file__))
    load_file = os.path.join(current_directory,'../data/time_series/{0}'.format(filename))
    results = []
    with open(load_file) as csvfile:
        results = [float(s) for line in csvfile.readlines() for s in line[:-1].split(',')]
    #create new load shape
    dss.LoadShape.New('PV')
    dss.LoadShape.Name('PV')
    dss.LoadShape.HrInterval(1)
    dss.LoadShape.Npts(len(results))
    dss.LoadShape.PMult(results)
    
    return dss    

def addPVSystem(dss, bus, inverter, capacity, irradiance, run_type, timeseries):
    #add the solar irradiance curve
    addSolarTimeSeries(dss,timeseries)
    #basic parameter curves
    dss.run_command("New XYCurve.PVPT npts=4 xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6]")
    dss.run_command("New XYCurve.PVeff npts=4  xarray=[.1  .2  .4  1.0]  yarray=[.86  .9  .93  .97]")
    dss.run_command("new XYCurve.vvarcurve Npts=4 Xarray=[0.5 0.95 1.05 1.5] Yarray=[1.0 1.0 -1.0 -1.0]")
    dss.run_command("new XYCurve.vwattcurve Npts=4 Xarray=[0.5 1 1.1 2] Yarray=[1.0 1.0 0 0]")
    dss.run_command(
    'New PVsystem.{0} Bus1={0} kVA={1} Pmpp={2} irradiance={3} phases=3 %Cutout = 0.0, %Cutin = 0.0, kv=24 Tyear=PVtemp P-Tcurve=PVPT effcurve=PVeff temperature=25 {4}=PV'.format(
        bus,
        inverter,
        capacity,
        irradiance,
        run_type))

    for pvsystem in dss.PVsystems.AllNames():
        dss_command_v = 'New monitor.PVsystem_voltage element=PVsystem.{0} term=1 mode=32'.format(pvsystem)
        dss.run_command(dss_command_v)
        dss_command_p = 'New monitor.PVsystem_power element=PVsystem.{0} term=1 mode=33 Ppolar=no'.format(pvsystem)
        dss.run_command(dss_command_p)
    
    return dss

def addStorageTimeSeries(dss,filename):
    #Read Time Series CSV file
    current_directory = os.path.realpath(os.path.dirname(__file__))
    load_file = os.path.join(current_directory,'../data/time_series/{0}'.format(filename))
    results = []
    with open(load_file) as csvfile:
        results = [float(s) for line in csvfile.readlines() for s in line[:-1].split(',')]
    
    #create new load shape
    dss.LoadShape.New('BSS')
    dss.LoadShape.Name('BSS')
    dss.LoadShape.HrInterval(1)
    dss.LoadShape.Npts(len(results))
    dss.LoadShape.PMult(results)
    
    return dss  

def addBSSystem(dss, bus, power, energy, run_type, timeseries):
    #add follow curve
    addStorageTimeSeries(dss, timeseries)
    #basic parameter curves
    dss.run_command('New Storage.Battery phases=3 Bus1={0} kV=24 kWrated={1} kWhrated={2} %reserve=10 kWhstored=382.233 dispmode=follow {3}=BSS'.format(
        bus,
        power,
        energy,
        run_type))
    
    dss_command_v = 'New monitor.BSS_voltage element=Storage.Battery term=1 mode=32'
    dss.run_command(dss_command_v)
    dss_command_i = 'New monitor.BSS_internal element=Storage.Battery term=1 mode=3'
    dss.run_command(dss_command_i)
    
    return dss

def monitor2df(dss, monitor_name):
    df = dss.utils.monitors_to_dataframe()
    dss.run_command("Export monitors {0}".format(monitor_name))
    file = df.loc[monitor_name]['FileName']
    mon_df = pd.read_csv(file)
    return mon_df