# -*- coding: utf-8 -*-
"""
Created on Tue Nov 07 13:39:54 2017

@author: dfberenson
"""

from skimage import io, filters, morphology, measure, util
import scipy.ndimage as nd
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

start_time = time.clock()
print('\nLoading images...\n')

#Open two-color microscopy image
micrograph_filename = r'E:\Ilastik Tracking\TestImage.tif'
micrograph_stack = io.imread(micrograph_filename)
[T,C,Y,X] = micrograph_stack.shape

#Open grayscale tracked image
tracked_filename = r'E:\Ilastik Tracking\Tracking.tiff'
tracked_stack = io.imread(tracked_filename)
[trackedT,trackedY,trackedX] = tracked_stack.shape

#Confirm stack sizes are compatible
if not (T == trackedT and Y == trackedY and X == trackedX):
    print('Stack sizes not matched')

print('\nImages Loaded\n')
print ('Time elapsed (s): '),
print (int(time.clock() - start_time))

#Get list of all cells and timepoints
highest_num_cell = np.max(tracked_stack)
all_cellnums = np.arange(1,highest_num_cell + 1)
all_timepoints = np.arange(0,T)

#Construct dataframe where each column is a cell, each row is a timepoint,
#and each entry is a Series containing the parameters to be measured (all 0 for now)
measurements_list = ['Lifespan','Mother','Daughter1','Daughter2','CentroidX','CentroidY',
'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','NetIntegratedIntensity_Chan1',
'MeanIntensity_Chan2','IntegratedIntensity_Chan2','NetIntegratedIntensity_Chan2']

s = pd.Series(np.zeros(len(measurements_list)), index = measurements_list)

df = pd.DataFrame(index = all_timepoints , columns = all_cellnums)
for index in df.index:
    for column in df.columns:
        df.loc[index][column] = pd.Series.copy(s)

print('\nDataFrame Created\n')
print ('Time elapsed (s): '),
print (int(time.clock() - start_time))

"""
At each timepoint, go through all cells and get info about them
Integrated and mean intensities, area, centroid coordinate, etc.
NB: Mistracked cells may get label 1
NB: Only works with exactly 2 channels on micrograph
"""

for t in all_timepoints:
    print('\nMeasuring cells for timepoint ' + str(t) + '\n')
    print ('Time elapsed (s): '),
    print (int(time.clock() - start_time))

    this_tracked_img = tracked_stack[t]
    [this_micrograph_Chan1,this_micrograph_Chan2] = micrograph_stack[t]
    
    for cell in all_cellnums:
        #Get Boolean matrix of which pixels correspond to this cell
        
        thisimg_currcell = (this_tracked_img == cell)
        
        #Make measurements about the cell
        [centroidY,centroidX] = [0,0]
        if np.any(thisimg_currcell):
            [centroidY,centroidX] = measure.regionprops(thisimg_currcell.astype(np.int))[0].centroid
            #Using this command
        
        area = sum(sum(thisimg_currcell))
        integratedintensity_Chan1 = sum(this_micrograph_Chan1[thisimg_currcell])
        integratedintensity_Chan2 = sum(this_micrograph_Chan2[thisimg_currcell])
        if not area == 0:
            meanintensity_Chan1 = integratedintensity_Chan1 / area
            meanintensity_Chan2 = integratedintensity_Chan2 / area
        
        thesemeasurements = df.loc[t][cell]
        thesemeasurements['Lifespan'] = np.nan
        thesemeasurements['Mother'] = np.nan
        thesemeasurements['Daughter1'] = np.nan
        thesemeasurements['Daughter2'] = np.nan
        thesemeasurements['CentroidX'] = centroidX
        thesemeasurements['CentroidY'] = centroidY
        thesemeasurements['Area'] = area
        thesemeasurements['MeanIntensity_Chan1'] = meanintensity_Chan1
        thesemeasurements['IntegratedIntensity_Chan1'] = integratedintensity_Chan1
        thesemeasurements['NetIntegratedIntensity_Chan1'] = np.nan
        thesemeasurements['MeanIntensity_Chan2'] = meanintensity_Chan2
        thesemeasurements['IntegratedIntensity_Chan2'] = integratedintensity_Chan2
        thesemeasurements['NetIntegratedIntensity_Chan2'] = np.nan
        
print ('\n\nTotal time elapsed (s): '),
print (int(time.clock() - start_time))



#Write another variant using dictionary of cells, each storing a matrix of times and measurements
#See which is faster