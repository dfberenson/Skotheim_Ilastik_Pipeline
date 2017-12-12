# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 12:09:13 2017

@author: dfberenson
"""

import numpy as np
import pandas as pd
import pickle, copy
from convertIlastikCSV import convertIlastikCsvToDataFrame
from Track import Track
from TrackGUI import TrackGui

class Experiment(object):

    def __init__(self, ilastik_csv_fpath = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini_NoLearning_Metadata.csv',
                 ilastik_image_fpath = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini-trackedNoLearning.tiff'):
        
        self.ilastik_csv_fpath = ilastik_csv_fpath
        self.ilastik_image_fpath = ilastik_image_fpath
        self.orig_df = convertIlastikCsvToDataFrame(self.ilastik_csv_fpath)
        
        self.trackIds_list = self.orig_df.columns.get_level_values('cell number').unique()
        self.measurements_list = ['Lineage','Lifespan','Mother','DaughterA','DaughterB','CentroidX','CentroidY',
        'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
        'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']
        
        cellsXmeasurements = pd.MultiIndex.from_product([self.trackIds_list,self.measurements_list],
                                                    names = ['cell number','measurement'])
        self.new_df = pd.DataFrame(index = self.orig_df.index, columns = cellsXmeasurements)
        self.new_df.sort_index(axis = 'columns', inplace = True)
        self.tracks_list = pd.Series(index = self.trackIds_list)
        self.individual_dfs_list = pd.Series(index = self.trackIds_list)
        
        self.all_trackpoints = []

        for trackId in self.trackIds_list:
            first_frame = min(self.orig_df[~np.isnan(self.orig_df.loc[:,(trackId,'Lineage')])].index)
                #Using 'Lineage' as an example, find the first frame (index) at which there is a non-NaN value.
            thistrack = Track(self, self.orig_df, trackId, first_frame)
                #Create and propagate a new Track. Note that if this is the Track for a daughter cell,
                #it will have its own brand new set of TrackPoints that contain the same info as the mother Track's TrackPoints,
                #but are different objects and will need to be treated independently. This is possibly not the best way to do it.
            self.tracks_list.loc[trackId] = thistrack
            thistrack_df = thistrack.toDataFrame()   
            self.new_df.loc[thistrack_df.index, thistrack_df.columns] = thistrack_df

    def addTrackpoint(self, trackpoint):
        self.all_trackpoints.append(trackpoint)
    
    def createTrackGui(self, tracknum, first_frame, stack_length):
        return TrackGui(self, tracknum, first_frame, stack_length)
    
    def getMatchingTrackpoints(self, frame, lineage):
        '''
        Lineage should perhaps be changed to LabelId as part of a larger overhaul
        that takes advantage of the information in LabelId
        '''
        matching_trackpoints = []
        for tp in self.all_trackpoints:
            if tp.frame == frame and tp.Lineage == lineage:
                matching_trackpoints.append(tp)
        return matching_trackpoints
        
    @staticmethod
    def areEqualDataFrames(df1, df2):
        '''
        Due to stuipd data typing problems, pd.DataFrame.equals() can return False rather than True
        when comparing two dataframes. This method compares row-wise rather than also column-wise.
        '''
        are_equal = True
        are_equal = min(are_equal, isinstance(df1, pd.DataFrame), isinstance(df2, pd.DataFrame))
        if not are_equal:
            return False
        are_equal = min(are_equal, df1.index.equals(df2.index))
        are_equal = min(are_equal, df1.columns.equals(df2.columns))
        if not are_equal:
            return False
        for i in df1.index:
            are_equal = min(are_equal, df1.loc[i].equals(df2.loc[i]))
        return are_equal
        
        
        
expt = Experiment()
o = expt.orig_df
n = expt.new_df
print(Experiment.areEqualDataFrames(o,n))

g = expt.createTrackGui(tracknum = 2, first_frame = 0, stack_length = 4)


#saved_filename = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\SavedData.pickle'
#
#with open(saved_filename,'wb') as f:
#    pickle.dump(expt,f)

#with open(saved_filename,'rb') as f:
#    expt = pickle.load(f)