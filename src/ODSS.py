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
    dss.run_command("clear")
    dss.run_command('compile {master}'.format(master=master_file))

    return dss


def DSSrunsnap(dss, show = False):
    dss.run_command('set MarkPVSystems=y')
    dss.run_command('set mode=snap')
    dss.run_command('Solve')

    if show == True:
        dss.run_command('show voltages LN Nodes')

    return dss


def addPVSystem(dss, bus='240_head', inverter=1200, capacity=1000, panel_eff=1.021):
    #basic parameter curves
    dss.run_command("New XYCurve.PVPT npts=4 xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6]")
    dss.run_command("New XYCurve.PVeff npts=1  xarray=[1]  yarray=[0.96]")
    dss.run_command("new XYCurve.vvarcurve Npts=4 Xarray=[0.5 0.95 1.05 1.5] Yarray=[1.0 1.0 -1.0 -1.0]")
    dss.run_command("new XYCurve.vwattcurve Npts=4 Xarray=[0.5 1 1.1 2] Yarray=[1.0 1.0 0 0]")

    dss.run_command(
    'New PVsystem.{0} Bus1={0} kVA={1} Pmpp={2} irradiance={3} phases=3 kv=24 Tyear=PVtemp P-Tcurve=PVPT effcurve=PVeff temperature=25 Varfollowinverter=true'.format(
        bus,
        inverter,
        capacity,
        panel_eff))

    return dss


def addStorage(dss, bus='240_head', power=750, energy=2100):
    dss.run_command(
    'New Storage.Battery phases=3 Bus1={0} kV=24 kw=0 kWrated={1} kWhrated={2} %EffCharge= dispmode=follow hourly=batteryshape'.format(
        bus,
        power,
        energy) )

    return dss


"""
def DSSTimeSeries(dict):
    new loadshape.diaIrradiance interval=1 Npts=8760 mult=(File='sam_PV_irr.csv') action=normalize


"""