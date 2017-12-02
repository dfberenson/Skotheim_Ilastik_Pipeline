# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:56:56 2017

@author: Skotheim Lab
"""

import pandas as pd
import numpy as np
import time

t0 = time.clock()

ilastik_csv_fpath = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini_NoLearning_Metadata.csv'
ilastik_csv = pd.read_csv(ilastik_csv_fpath)

all_timepoints = np.unique(ilastik_csv['frame'])
all_tracks = np.unique(ilastik_csv['trackId'])

ilastik_pivot = ilastik_csv.pivot_table(index = 'frame', columns = 'trackId', values =
                                ['lineageId','parentTrackId','Center_of_the_object_0','Center_of_the_object_1',
                                'Size_in_pixels_0','Mean_Intensity_0','Mean_Intensity_1','Total_Intensity_0','Total_Intensity_1'])


measurements_list = ['Lineage','Lifespan','Mother','Daughter1','Daughter2','CentroidX','CentroidY',
    'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
    'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']

cellsXmeasurements = pd.MultiIndex.from_product([all_tracks,measurements_list],
                                                names = ['cell number','measurement'])
df = pd.DataFrame(index = all_timepoints, columns = cellsXmeasurements)
df.index.name = 'frame'
df.sort_index(axis = 'columns', inplace = True)

for track in all_tracks:
    
    df.loc[:,(track,'Lineage')] = ilastik_pivot.loc[:,('lineageId',track)]
    df.loc[:,(track,'CentroidX')] = ilastik_pivot.loc[:,('Center_of_the_object_0',track)]
    df.loc[:,(track,'CentroidY')] = ilastik_pivot.loc[:,('Center_of_the_object_1',track)]
    df.loc[:,(track,'Area')] = ilastik_pivot.loc[:,('Size_in_pixels_0',track)]
    df.loc[:,(track,'MeanIntensity_Chan1')] = ilastik_pivot.loc[:,('Mean_Intensity_0',track)]
    df.loc[:,(track,'MeanIntensity_Chan2')] = ilastik_pivot.loc[:,('Mean_Intensity_1',track)]
    df.loc[:,(track,'IntegratedIntensity_Chan1')] = ilastik_pivot.loc[:,('Total_Intensity_0',track)]
    df.loc[:,(track,'IntegratedIntensity_Chan2')] = ilastik_pivot.loc[:,('Total_Intensity_1',track)]

for track in all_tracks:
    has_existed = False
    thistrack_lastframe = max(all_timepoints)
    for t in all_timepoints:
        #Find t where the track ceases to exist after having existed for a while
        if np.isnan(df.loc[t,(track,'Lineage')]) and not has_existed:
            continue
        
        if not np.isnan(df.loc[t,(track,'Lineage')]):
            has_existed = True
            
        if np.isnan(df.loc[t,(track,'Lineage')]) and has_existed:
            thistrack_lastframe = t-1
            print('Track ' + str(track) + ' divides at frame ' + str(thistrack_lastframe))
            break
    

    
    if thistrack_lastframe < max(all_timepoints):
        
        lin = df.loc[thistrack_lastframe,(track,'Lineage')]
        nextframe_df = df.loc[thistrack_lastframe+1]
        unstacked = nextframe_df.unstack()
        tracks = unstacked[unstacked.loc[:,'Lineage'] == lin].index
        
                           
        if len(tracks) > 2:
           print('Track {} splits into {} tracks at frame {}'
                 .format(track,len(tracks),thistrack_lastframe))
          
        '''
        NEED TO DEAL WITH WHAT HAPPENS WHEN THERE ARE >2 DESCENDANTS FROM SAME LINEAGE
        E.G., FRAME 36 WHEN CELL 9 SPLITS INTO 10 AND 11 BUT 8 ALREADY EXISTS
        '''
        
        if len(tracks) == 2:
            daughter1 = tracks[0]
            daughter2 = tracks[1]
            
            df.loc[thistrack_lastframe,(track,'Daughter1')] = daughter1
            df.loc[thistrack_lastframe,(track,'Daughter2')] = daughter2
                   
            df.loc[thistrack_lastframe+1,(daughter1,'Mother')] = track
            df.loc[thistrack_lastframe+1,(daughter2,'Mother')] = track
        


'''
Follow a lineage
'''
lin = 4

lineage_boolean_array = df.xs('Lineage',level='measurement',axis=1) == lin
tracknums_list = [None] * len(df.index)
tracknums_complete = []
num_traces = 0
for t in df.index:
    tracknums_list[t] = lineage_boolean_array.columns[lineage_boolean_array.loc[t]]
    tracknums_complete.extend(tracknums_list[t].tolist())
    num_traces = max(num_traces, sum(lineage_boolean_array.loc[t]))

tracknums_complete = np.unique(tracknums_complete)
tracknums_complete.sort()
subtrace_cellsXmeasurements = pd.MultiIndex.from_product([tracknums_complete,
                                                          df.columns.get_level_values('measurement').unique()],
                                                           names = ['cell number','measurement'])

subtrace_df = pd.DataFrame(index = df.index, columns = subtrace_cellsXmeasurements)
subtrace_df.sort_index(axis = 'columns', inplace = True)

##FILL IN NEW subtrace_df WITH DATA FROM df, DUPLICATING VALUES BEFORE SPLIT
##SO ALL TRACES HAVE COMPLETE DATA THROUGHOUT TIMECOURSE, PARENT AND BEYOND

def fill_ancestors(df, subtrace_df, t, track, ancestor = None):
    if ancestor == None:
        ancestor = track
    for meas in subtrace_df.columns.get_level_values('measurement').unique():
            subtrace_df.loc[t,(track,meas)] = df.loc[t,(ancestor,meas)]
            #Fill in column 'track' with data from 'ancestor' track
    print('Entered ancestor {} area {} for time {}'.format(ancestor,df.loc[t,(ancestor,'Area')],t))        
    if t > min(df.index):
        mother = df.loc[t,(track,'Mother')]
        if np.isnan(mother):
            fill_ancestors(df, subtrace_df, t-1, track, ancestor)
            #If the cell wasn't born at this point, continue tracing backwards
            #using the same ancestor as before
        else: 
            print('found mother {} at time {}'.format(mother,t))
            fill_ancestors(df, subtrace_df, t-1, track = track, ancestor = mother)
            #If the cell was born at this point, continue tracing backwards
            #using the new mother as the ancestor
    else:
        return


for final_daughter in tracknums_list[max(df.index)]:
    fill_ancestors(df, subtrace_df, max(df.index), final_daughter)
    


'''
Plot lineage centriod motion
'''

print(time.clock() - t0)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

times = df.index

