#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 13:42:13 2018

@author: jdlara
"""
import os
import sys
module_path = os.path.abspath(os.path.join('.','src'))
if module_path not in sys.path:
    sys.path.append(module_path)
  
from DCymetoDSS import CymeToDSS
import ODSS as DSS    

system = DSS.loadDSS()
system = DSS.addPVSystem(system)
system.utils.class_to_dataframe('PVsystem')
system = DSS.addStorage(system)
system.utils.class_to_dataframe('Storage')


system.LoadShape.New("load")


import opendssdirect as dss

import os

dss.run_command('compile {master}'.format(master='master.dss'))
dss.run_command('New Storage.Battery phases=3 Bus1=240_head kV=24 kw=0 kWrated=750.0 kWhrated=2100.0 %EffCharge= dispmode=follow hourly=batteryshape')
dss.utils.class_to_dataframe('Storage')
dss.LoadShape.New("load")