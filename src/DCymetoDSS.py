#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 15:43:58 2018

@author: Jose Daniel
"""
import os
import time

#Import the CYME reader
from ditto.readers.cyme.read import Reader

#Import the OpenDSS writer
from ditto.writers.opendss.write import Writer

#Import Store
from ditto.store import Store

def CymeToDSS():
    '''
    CYME ---> OpenDSS example.
    '''

    #Path settings (assuming it is run from examples folder)
    #Change this if you wish to use another system
    current_directory = os.path.realpath(os.path.dirname(__file__))
    input_path = os.path.join(current_directory,'../data/Cyme_Files')


    ############################
    #  STEP 1: READ FROM CYME  #
    ############################
    #
    #Create a Store object
    print('>>> Creating empty model...')
    model = Store()

    #Instanciate a Reader object
    r = Reader(data_folder_path = input_path)

    #Parse (can take some time for large systems...)
    print('>>> Reading from CYME...')
    start = time.time() #basic timer
    r.parse(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))

    ##############################
    #  STEP 2: WRITE TO OpenDSS  #
    ##############################
    #
    #Instanciate a Writer object
    output_path = os.path.join(current_directory,'../data/DSS_files')
    w = Writer(output_path = output_path)

    #Write to OpenDSS (can also take some time for large systems...)
    print('>>> Writing to OpenDSS...')
    start = time.time() #basic timer
    w.write(model)
    end = time.time()
    print('...Done (in {} seconds'.format(end-start))