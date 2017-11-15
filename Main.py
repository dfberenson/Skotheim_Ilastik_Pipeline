# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 11:51:20 2017

@author: dfberenson
"""


from skimage import io, filters, morphology, measure, util
import scipy.ndimage as nd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import copy

start_time = time.clock()
expt = Experiment('Test')

print('\nConstructing dataframe...\n')
expt.construct_dataframe()
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

c = copy.deepcopy(expt)
#expt = copy.deepcopy(c)

print('\nCalculating smoothening...\n')
expt.smoothen('NetIntegratedIntensity_Chan1')
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating speed...\n')
expt.calculate_speed()
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating neighbors...\n')
expt.calculate_num_neighbors(100)
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating derivative...\n')
expt.calculate_derivative('NetIntegratedIntensity_Chan1')
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating relative derivative...\n')
expt.calculate_relative_derivative('NetIntegratedIntensity_Chan1')
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

'''
ToDo:
Run Ilastik in headless mode:
http://ilastik.org/documentation/basics/headless.html
https://github.com/ilastik/ilastik/issues/1519    
    
Import lineage data from ilastik
Construct lineage traces using something like Experiment.get_stitched_tracks()
Generate plots

'''




'''
BEFORE CONVERTED TRACKINGDATAFRAME TO CLASS
print('\nConstructing dataframe...\n')
df = construct_dataframe()
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating speed...\n')
df = calculate_speed(df)
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating neighbors...\n')
df = calculate_num_neighbors(df,100)
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating derivative...\n')
df = calculate_derivative(df,'NetIntegratedIntensity_Chan1')
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))

print('\nCalculating relative derivative...\n')
df = calculate_relative_derivative(df,'NetIntegratedIntensity_Chan1')
print('\nTotal time elapsed (s): ')
print (int(time.clock() - start_time))
'''