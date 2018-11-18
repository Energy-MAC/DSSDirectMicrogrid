#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 20:45:25 2018

@author: jdlara
"""

import opendssdirect as dss
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
        dss.run_command('show voltages LN Nodes')

    return dss

def DSSrunts(dss, show = False):
    dss.run_command('set mode=daily')
    dss.run_command('set stepsize=1h')
    dss.run_command('Solve')

    if show == True:
        dss.run_command('show voltages LN Nodes')

    return dss

def addMonitors(dss):
    for load in dss.Loads.AllNames():
        dss_command_v = 'New monitor.{0}_voltage element=Load.{0} term=1 mode=0 Ppolar=no'.format(load)
        dss.run_command(dss_command_v)
        dss_command_p = 'New monitor.{0}_power element=Load.{0} term=1 mode=1 Ppolar=no'.format(load)
        dss.run_command(dss_command_p)
    
    for sources in dss.Vsources.AllNames():
        dss_command_v = 'New monitor.{0}_voltage element=Vsource.{0} term=1  mode=0 Ppolar=no'.format(sources)
        dss.run_command(dss_command_v)
        dss_command_p = 'New monitor.{0}_power element=Vsource.{0} term=1 mode=1 Ppolar=no'.format(sources)
        dss.run_command(dss_command_p)
    
    return dss 

def addLoadTimeSeries(dss,filename = 'load_shape.csv'):
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
    dss.LoadShape.Npts(24)
    dss.LoadShape.PMult(results)
    
    #assign the load shape to all loads
    for l in Iterator(dss.Loads,'Daily'):
        l('load')
    
    return dss
 
def addSolarTimeSeries(dss,filename = 'PV_shape.csv'):
    #Read Time Series CSV file
    current_directory = os.path.realpath(os.path.dirname(__file__))
    load_file = os.path.join(current_directory,'../data/time_series/load_shape.csv')
    results = []
    with open(load_file) as csvfile:
        results = [float(s) for line in csvfile.readlines() for s in line[:-1].split(',')]
    
    #create new load shape
    dss.LoadShape.New('PV')
    #dss.LoadShape.Name('load')
    dss.LoadShape.HrInterval(1)
    dss.LoadShape.Npts(24)
    dss.LoadShape.PMult(results)
    
    return dss    

def addPVSystem(dss, bus='240_head', inverter=1200, capacity=1000, panel_eff=1.021):
    #add the solar irradiance curve
    addSolarTimeSeries(dss)
    #basic parameter curves
    dss.run_command("New XYCurve.PVPT npts=4 xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6]")
    dss.run_command("New XYCurve.PVeff npts=1  xarray=[1]  yarray=[0.96]")
    dss.run_command("new XYCurve.vvarcurve Npts=4 Xarray=[0.5 0.95 1.05 1.5] Yarray=[1.0 1.0 -1.0 -1.0]")
    dss.run_command("new XYCurve.vwattcurve Npts=4 Xarray=[0.5 1 1.1 2] Yarray=[1.0 1.0 0 0]")

    dss.run_command(
    'New PVsystem.{0} Bus1={0} kVA={1} Pmpp={2} irradiance={3} phases=3 kv=24 Tyear=PVtemp P-Tcurve=PVPT effcurve=PVeff temperature=25 Varfollowinverter=true, daily=PV'.format(
        bus,
        inverter,
        capacity,
        panel_eff))

    return dss