# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:56:56 2017

@author: Skotheim Lab
"""

import pandas as pd
import numpy as np

def convertIlastikCsvToDataFrame(ilastik_csv_fpath =
                                 r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini_NoLearning_Metadata.csv'):
   
    print('\nReading ilastik Csv...')
    ilastik_csv = pd.read_csv(ilastik_csv_fpath)
    
    all_timepoints = np.unique(ilastik_csv['frame'])
    all_trackIds = np.unique(ilastik_csv['trackId'])
    
    ilastik_pivot = ilastik_csv.pivot_table(index = 'frame', columns = 'trackId', values =
                                    ['lineageId','parentTrackId','Center_of_the_object_0','Center_of_the_object_1',
                                    'Size_in_pixels_0','Mean_Intensity_0','Mean_Intensity_1','Total_Intensity_0','Total_Intensity_1'])
    
    
    measurements_list = ['Lineage','Lifespan','Mother','DaughterA','DaughterB','CentroidX','CentroidY',
        'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
        'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']
    
    cellsXmeasurements = pd.MultiIndex.from_product([all_trackIds,measurements_list],
                                                    names = ['cell number','measurement'])
    df = pd.DataFrame(index = all_timepoints, columns = cellsXmeasurements)
    df.index.name = 'frame'
    df.sort_index(axis = 'columns', inplace = True)
    
    for trackId in all_trackIds:
        
        df.loc[:,(trackId,'Mother')] = ilastik_pivot.loc[:,('parentTrackId',trackId)]
        df.loc[:,(trackId,'Lineage')] = ilastik_pivot.loc[:,('lineageId',trackId)]
        df.loc[:,(trackId,'CentroidX')] = ilastik_pivot.loc[:,('Center_of_the_object_0',trackId)]
        df.loc[:,(trackId,'CentroidY')] = ilastik_pivot.loc[:,('Center_of_the_object_1',trackId)]
        df.loc[:,(trackId,'Area')] = ilastik_pivot.loc[:,('Size_in_pixels_0',trackId)]
        df.loc[:,(trackId,'MeanIntensity_Chan1')] = ilastik_pivot.loc[:,('Mean_Intensity_0',trackId)]
        df.loc[:,(trackId,'MeanIntensity_Chan2')] = ilastik_pivot.loc[:,('Mean_Intensity_1',trackId)]
        df.loc[:,(trackId,'IntegratedIntensity_Chan1')] = ilastik_pivot.loc[:,('Total_Intensity_0',trackId)]
        df.loc[:,(trackId,'IntegratedIntensity_Chan2')] = ilastik_pivot.loc[:,('Total_Intensity_1',trackId)]
    
    df[df.loc[slice(None),(slice(None),'Mother')] == 0] = np.nan
    #Replace '0' in the Mother column with NaN
              
    for trackId in all_trackIds:
        has_existed = False
        for t in all_timepoints:
            #Find t where the trackId ceases to exist after having existed for a while
            if np.isnan(df.loc[t,(trackId,'Lineage')]) and not has_existed:
                continue
            
            elif not np.isnan(df.loc[t,(trackId,'Lineage')]):
                has_existed = True
                
            elif np.isnan(df.loc[t,(trackId,'Lineage')]) and has_existed:
                thistrackId_lastframe = t-1
                print('TrackId ' + str(trackId) + ' divides at frame ' + str(thistrackId_lastframe))
                break
        
        else:           #This 'else' applies if the for loop ended by running completely through all_timepoints
            continue    #Then go to the next trackId, skipping the Daughter linking below
    
        #Link trackId to its daughters at the frame of division ('thistrackId_lastframe')
        lin = df.loc[thistrackId_lastframe,(trackId,'Lineage')]
        nextframe_df = df.loc[thistrackId_lastframe+1]
        unstacked = nextframe_df.unstack()
        potential_daughters = unstacked[unstacked.loc[:,'Lineage'] == lin].index
           
        num_genuine_daughters = 0
        for daughter in potential_daughters:
           mother = df.loc[thistrackId_lastframe+1,(daughter,'Mother')]
           if mother == trackId:          #If the Mother from the CSV is consistent with the current trackId
               num_genuine_daughters += 1
               if num_genuine_daughters == 1:
                   df.loc[thistrackId_lastframe,(trackId,'DaughterA')] = daughter
               elif num_genuine_daughters == 2:
                   df.loc[thistrackId_lastframe,(trackId,'DaughterB')] = daughter
               else:
                   raise ValueError('TrackId {} has {} genuine daughters at frame {}'
                     .format(trackId,num_genuine_daughters,thistrackId_lastframe))
    
    print('ilastik Csv import complete.\n')                     
    return df


def getLineageSubtracedDataframe(df, lin):
    '''
    Follow a lineage and return a mini Dataframe of its most distant descendants,
    with higher rows filled in from the ancestor. Tool for easy multigenerational tracing.
    '''
    lineage_boolean_array = df.xs('Lineage',level='measurement',axis=1) == lin
    trackIdnums_list = [None] * len(df.index)
    trackIdnums_complete = []
    num_traces = 0
    for t in df.index:
        trackIdnums_list[t] = lineage_boolean_array.columns[lineage_boolean_array.loc[t]]
        trackIdnums_complete.extend(trackIdnums_list[t].tolist())
        num_traces = max(num_traces, sum(lineage_boolean_array.loc[t]))
    
    trackIdnums_complete = np.unique(trackIdnums_complete)
    trackIdnums_complete.sort()
    
    final_daughters = trackIdnums_list[max(df.index)].sort_values()
    subtrace_cellsXmeasurements = pd.MultiIndex.from_product([final_daughters,
                                                              df.columns.get_level_values('measurement').unique()],
                                                               names = ['cell number','measurement'])
    
    subtrace_df = pd.DataFrame(index = df.index, columns = subtrace_cellsXmeasurements)
    subtrace_df.sort_index(axis = 'columns', inplace = True)
    for final_daughter in final_daughters:
        fill_ancestors(df, subtrace_df, max(df.index), final_daughter)
    
    return subtrace_df

##FILL IN NEW subtrace_df WITH DATA FROM df, DUPLICATING VALUES BEFORE SPLIT
##SO ALL TRACES HAVE COMPLETE DATA THROUGHOUT TIMECOURSE, PARENT AND BEYOND

def fill_ancestors(orig_df, subtrace_df, t, trackId, ancestor = None):
    if ancestor is None:
        ancestor = trackId
    for meas in subtrace_df.columns.get_level_values('measurement').unique():
            subtrace_df.loc[t,(trackId,meas)] = orig_df.loc[t,(ancestor,meas)]
            #Fill in column 'trackId' with data from 'ancestor' trackId
            
    #print('Entered ancestor {} area {} for time {}'.format(ancestor,orig_df.loc[t,(ancestor,'Area')],t))        
    if t > min(orig_df.index):
        mother = orig_df.loc[t,(trackId,'Mother')]
        if np.isnan(mother):
            fill_ancestors(orig_df, subtrace_df, t-1, trackId, ancestor)
            #If the cell wasn't born at this point, continue tracing backwards
            #using the same ancestor as before
        else: 
            print('found mother {} at time {}'.format(mother,t))
            fill_ancestors(orig_df, subtrace_df, t-1, trackId = trackId, ancestor = mother)
            #If the cell was born at this point, continue tracing backwards
            #using the new mother as the ancestor
    else:
        return