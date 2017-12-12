# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 18:52:38 2017

@author: dfberenson
"""

import numpy as np
import pandas as pd
from TrackPoint import TrackPoint

class Track(object):
    
    def __init__(self, expt, df, trackId, init_frame = None):
        
        self.expt = expt
        self.df = df
        self.trackId = trackId
        
        if init_frame is not None:
            self.init_frame = init_frame
        
        self.init_trackpoint = TrackPoint(self, self.init_frame, None)
        print('\n')
        self.init_trackpoint.propagate_trackpoint()
        self.getLifespan()
        
    def getLifespan(self):
        
        curr_trackpoint = self.init_trackpoint
        while curr_trackpoint.next_trackpoint is not None:
            curr_trackpoint = curr_trackpoint.next_trackpoint
        self.last_trackpoint = curr_trackpoint
        self.last_frame = self.last_trackpoint.frame
        self.lifespan = self.last_frame - self.init_frame
        return self.lifespan


    def toDataFrame(self, measurements_list = ['Lineage','Lifespan','Mother','DaughterA','DaughterB','CentroidX','CentroidY',
        'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
        'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']):
        
        self.getLifespan()
        idx = np.arange(self.init_frame, self.last_frame + 1)
        new_df = pd.DataFrame(index = idx, columns = pd.MultiIndex.from_product([[self.trackId],measurements_list],
                                                    names = ['cell number','measurement']))
        new_df.index.name = 'frame'
        new_df.sort_index(axis = 'columns', inplace = True)
        
        curr_trackpoint = self.init_trackpoint
        while curr_trackpoint is not None:
            frame = curr_trackpoint.frame
            new_df.loc[frame,(self.trackId,'Mother')] = np.float64(curr_trackpoint.Mother)
            new_df.loc[frame,(self.trackId,'DaughterA')] = np.float64(curr_trackpoint.DaughterA)
            new_df.loc[frame,(self.trackId,'DaughterB')] = np.float64(curr_trackpoint.DaughterB)
            new_df.loc[frame,(self.trackId,'Lineage')] = np.float64(curr_trackpoint.Lineage)
            new_df.loc[frame,(self.trackId,'CentroidX')] = np.float64(curr_trackpoint.CentroidX)
            new_df.loc[frame,(self.trackId,'CentroidY')] = np.float64(curr_trackpoint.CentroidY)
            new_df.loc[frame,(self.trackId,'Area')] = np.float64(curr_trackpoint.Area)
            new_df.loc[frame,(self.trackId,'MeanIntensity_Chan1')] = np.float64(curr_trackpoint.MeanIntensity_Chan1)
            new_df.loc[frame,(self.trackId,'MeanIntensity_Chan2')] = np.float64(curr_trackpoint.MeanIntensity_Chan2)
            new_df.loc[frame,(self.trackId,'IntegratedIntensity_Chan1')] = np.float64(curr_trackpoint.IntegratedIntensity_Chan1)
            new_df.loc[frame,(self.trackId,'IntegratedIntensity_Chan2')] = np.float64(curr_trackpoint.IntegratedIntensity_Chan2)
            curr_trackpoint = curr_trackpoint.next_trackpoint
        
        return new_df
    
    def getImStack_and_TrackPointStack(self, first_frame, stack_length):
        '''
        Starting from init_frame, return an image stack and a list of TrackPoints with length 'length'.
        Does not work with branched (dividing) tracks.
        TBD: image should be recolored to highlight the tracked objects.
        '''
        stack_first_trackpoint = self.init_trackpoint
        
        for i in range(first_frame):
            stack_first_trackpoint = stack_first_trackpoint.next_trackpoint
            assert stack_first_trackpoint is not None
        
        centX = stack_first_trackpoint.CentroidX
        centY = stack_first_trackpoint.CentroidY
        first_img = stack_first_trackpoint.getImage(centX = centX, centY = centY)
        this_trackpoint = stack_first_trackpoint
        im_stack = np.array([first_img] * stack_length) #Initialize image stack of right size.
        trackpoint_stack = [None] * stack_length #Initialize trackpoint stack of right size.
                           
        for i in range(stack_length):
            trackpoint_stack[i] = this_trackpoint
            this_img = this_trackpoint.getImage(centX = centX, centY = centY)
            im_stack[i] = this_img
            this_trackpoint = this_trackpoint.next_trackpoint
        
        return (im_stack,trackpoint_stack)
            
    
    def visualizeStructure(self):
        '''
        TBD: maybe can do something here to show all the TrackPoints the Track goes through?
        '''
        pass
    
    
    def __str__(self):
        return '<<Track object with trackId {} starting at frame {} ending at frame {}.>>'.format(self.trackId, self.init_frame, self.last_frame)
    
    __repr__ = __str__