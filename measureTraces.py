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
tracked_filename = r'E:\Ilastik Tracking\Tracking_2.tiff'
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


#Construct multiindexed dataframe where each row is a timepoint and each column
#is multi-indexed with cell number and measurement type. All values set to nan.

measurements_list = ['Lifespan','Mother','Daughter1','Daughter2','CentroidX','CentroidY',
'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']

cellsXmeasurements = pd.MultiIndex.from_product([all_cellnums,measurements_list],
                                                names = ['cell number','measurement'])
df = pd.DataFrame(index = all_timepoints, columns = cellsXmeasurements)
df.index.name = 'time'

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
            #measure.regionprops is faster
        
        area = sum(sum(thisimg_currcell))
        integratedintensity_Chan1 = sum(this_micrograph_Chan1[thisimg_currcell])
        integratedintensity_Chan2 = sum(this_micrograph_Chan2[thisimg_currcell])
        if not area == 0:
            meanintensity_Chan1 = float(integratedintensity_Chan1) / area
            meanintensity_Chan2 = float(integratedintensity_Chan2) / area

        mean_local_background_Chan1 = get_mean_local_background(this_micrograph_Chan1, this_tracked_img, centroidX, centroidY)
        mean_local_background_Chan2 = get__mean_local_background(this_micrograph_Chan2, this_tracked_img, centroidX, centroidY)

        #Record measurements into dataframe
        thesemeasurements = df.loc[t,cell]
        thesemeasurements['Lifespan'] = np.nan
        thesemeasurements['Mother'] = np.nan
        thesemeasurements['Daughter1'] = np.nan
        thesemeasurements['Daughter2'] = np.nan
        thesemeasurements['CentroidX'] = centroidX
        thesemeasurements['CentroidY'] = centroidY
        thesemeasurements['Area'] = area
        thesemeasurements['MeanIntensity_Chan1'] = meanintensity_Chan1
        thesemeasurements['IntegratedIntensity_Chan1'] = integratedintensity_Chan1
        thesemeasurements['MeanLocalBackground_Chan1'] = mean_local_background_Chan1
        thesemeasurements['NetIntegratedIntensity_Chan1'] = integratedintensity_Chan1 - mean_local_background_Chan1*area
        thesemeasurements['MeanIntensity_Chan2'] = meanintensity_Chan2
        thesemeasurements['IntegratedIntensity_Chan2'] = integratedintensity_Chan2
        thesemeasurements['MeanLocalBackground_Chan2'] = mean_local_background_Chan2
        thesemeasurements['NetIntegratedIntensity_Chan2'] = integratedintensity_Chan2 - mean_local_background_Chan2*area
        
print ('\n\nTotal time elapsed (s): '),
print (int(time.clock() - start_time))



def get_mean_local_background(micrograph, tracked_img, x, y):
    
    [Y,X] = micrograph.shape
    x1 = min(0,x-200)
    x2 = max(X,x+200)
    y1 = min(0,y-200)
    y2 = max(Y,y+200)
    
    cropped_micrograph = micrograph[y1:y2,x1:x2]
    cropped_tracked_img = tracked_img[y1:y2,x1:x2]
    
    cropped_nocells = (cropped_tracked_img == 0)
    empty_area = sum(sum(cropped_nocells))
    empty_integratedintensity = sum(cropped_micrograph(cropped_nocells))
    if not empty_area == 0:
        empty_meanintensity = float(empty_integratedintensity)/empty_area
    
    return empty_meanintensity
    
    

