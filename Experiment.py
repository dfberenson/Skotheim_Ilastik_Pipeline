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
    '''
    The Experiment class represents all the information about a particular timelapse imaging experiment.
    Namely: a DataFrame with the original data from the ilastik-produced CSV;
    a DataFrame produced by reconstruction from the Track and TrackPoint hierarchies
    (which would be different from the original iff changes to the tracking were made by the user);
    a Series of Track objects corresponding to cell lifespans;
    and a List of all the TrackPoint objects created during Track propagation
    (see Track and TrackPoint class documentation).
    
    
    '''

    def __init__(self, ilastik_csv_fpath = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini_NoLearning_Metadata.csv',
                 ilastik_image_fpath = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\TestImage2_SuperMini-trackedNoLearning.tiff'):
        
        self.ilastik_csv_fpath = ilastik_csv_fpath
        self.ilastik_image_fpath = ilastik_image_fpath
        self.orig_df = convertIlastikCsvToDataFrame(self.ilastik_csv_fpath)
            #Create a DataFrame with the data from the CSV
        
        self.trackIds_list = self.orig_df.columns.get_level_values('cell number').unique()
        self.measurements_list = ['Lineage','Lifespan','Mother','DaughterA','DaughterB','CentroidX','CentroidY',
        'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
        'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']
        
        cellsXmeasurements = pd.MultiIndex.from_product([self.trackIds_list,self.measurements_list],
                                                    names = ['cell number','measurement'])
        self.new_df = pd.DataFrame(index = self.orig_df.index, columns = cellsXmeasurements)
        self.new_df.sort_index(axis = 'columns', inplace = True)
            #Sorting DataFrame index is necessary to allow effective slicing.
        self.tracks_list = pd.Series(index = self.trackIds_list)
        self.individual_dfs_list = pd.Series(index = self.trackIds_list)
        
        self.all_trackpoints = []

        for trackId in self.trackIds_list:
            first_frame = min(self.orig_df[~np.isnan(self.orig_df.loc[:,(trackId,'Lineage')])].index)
                #Using 'Lineage' as an example datum, find the first frame (index) at which there is a non-NaN value.
            thistrack = Track(self, self.orig_df, trackId, first_frame)
                #Create and propagate a new Track. Note that if this is the Track for a daughter cell,
                #it will have its own brand new set of TrackPoints that contain the same info as the mother Track's TrackPoints,
                #but are different objects and will need to be treated independently. ToDo: possibly this architecture should be changed.
            self.tracks_list.loc[trackId] = thistrack
            thistrack_df = thistrack.toDataFrame()   
            self.new_df.loc[thistrack_df.index, thistrack_df.columns] = thistrack_df
                #Add the DataFrame substructure from this Track to the larger new DataFrame.

    def addTrackpoint(self, trackpoint):
        '''
        Add a TrackPoint to the list of TrackPoints stored in the Experiment object.
        '''
        self.all_trackpoints.append(trackpoint)
    
    def createTrackGui(self, tracknum, first_frame, stack_length):
        '''
        Allows convenient calling of TrackGui constructor. Returns the TrackGui object.
        '''
        return TrackGui(self, tracknum, first_frame, stack_length)
    
    def getMatchingTrackpoints(self, frame, lineage):
        '''
        Using the stored list of TrackPoints, return a list of TrackPoints that match the passed frame and lineage numbers.
        ToDo: Really should look for matching LabelId rather than Lineage because sister cells share a Lineage,
        and information about mergers is most accurately reflected in LabelId rather than TrackId.
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
        when comparing two equal dataframes when one has ints and one has floats.
        This new method compares the DataFrames only row-wise, rather than also column-wise.
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
        
'''
MAIN:
    Create a new Experiment.
    Confirm that the DataFrame imported directly from the CSV and the DataFrame recreated from the TrackPoint lineages are equivalent.
    Create a GUI.
    Pickle the Experiment.
'''
        
expt = Experiment()
o = expt.orig_df
n = expt.new_df
print(Experiment.areEqualDataFrames(o,n))

g = expt.createTrackGui(tracknum = 2, first_frame = 0, stack_length = 4)


saved_filename = r'C:\Users\Skotheim Lab\Desktop\Ilastik Tracking\SavedData.pickle'

with open(saved_filename,'wb') as f:
    pickle.dump(expt,f)

#with open(saved_filename,'rb') as f:
#    expt = pickle.load(f)