# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 19:01:23 2017

@author: dfberenson
"""
import numpy as np
import pandas as pd
from skimage import io
import matplotlib.pyplot as plt

class TrackPoint(object):
    
    def __init__(self, track, frame, previous_trackpoint, isNewborn = False, newTrackId = None):
        '''
        Creates a TrackPoint object corresponding to a single tracked object at a single timepoint.
        Uses the data from the Track's Experiment's DataFrame to assign properties of this individial TrackPoint.
        Arguments:
            track = Track object to which this TrackPoint object belongs.
            frame = int corresponding to the timepoint that can be looked up in the dataframe.
            previous_trackpoint = TrackPoint object for the same Tracked cell in the previous timepoint.
            isNewborn = Boolean indicating whether or not this TrackPoint is the immediate product of cell division.
            newTrackId = int corresponding to a new trackId that would be assigned at birth. If not passed to the constructor,
            the previous_trackpoint's trackId will be used.
        '''
        self.track = track
        self.expt = self.track.expt
        self.expt.addTrackpoint(self)
        df = track.df
        self.frame = frame
        self.isLast = (self.frame == max(df.index))
        self.previous_trackpoint = previous_trackpoint
        self.next_trackpoint = None
        
        #Get the trackId from the original Track, then overwrite from the previous TrackPoint or the Constructor args
        self.trackId = self.track.trackId
        if self.previous_trackpoint is not None:
            self.trackId = self.previous_trackpoint.trackId
        if newTrackId is not None:
            self.trackId = newTrackId
           
        self.isNewborn = isNewborn
        if self.isNewborn:
            self.mother_trackpoint = self.previous_trackpoint
        
        self.isDividing = False  #Will check downstream if should be set to True
        self.daughterA_trackpoint = None
        self.daughterB_trackpoint = None
  
        #Look back at DataFrame to figure out what the measurements were about this cell at this time.
        self.Lineage = df.loc[frame,(self.trackId,'Lineage')]
        self.Mother = df.loc[frame,(self.trackId,'Mother')]
        self.DaughterA = df.loc[frame,(self.trackId,'DaughterA')]
        self.DaughterB = df.loc[frame,(self.trackId,'DaughterB')]
        if not np.isnan(self.DaughterA) or not np.isnan(self.DaughterB):
            self.isDividing = True
        self.Area = df.loc[frame, (self.trackId,'Area')]
        self.MeanIntensity_Chan1 = df.loc[frame ,(self.trackId,'MeanIntensity_Chan1')]
        self.MeanIntensity_Chan2 = df.loc[frame ,(self.trackId,'MeanIntensity_Chan2')]
        self.IntegratedIntensity_Chan1 = df.loc[frame ,(self.trackId,'IntegratedIntensity_Chan1')]
        self.IntegratedIntensity_Chan2 = df.loc[frame ,(self.trackId,'IntegratedIntensity_Chan2')]
        self.CentroidX = df.loc[frame ,(self.trackId,'CentroidX')]
        self.CentroidY = df.loc[frame ,(self.trackId,'CentroidY')]
   

    def propagate_trackpoint(self):
        '''
        Recursive method to propagate the linked TrackPoints through time.
        First checks to see if this TrackPoint is from the very last frame of the movie and, if yes, terminates the recursion.
        Note that it does NOT currently handle a Track ending due to exiting the image frame.
        If the current TrackPoint is not dividing, create a new TrackPoint properly linked to this one, then call propagate_trackpoint again on the new one.
        If the current TrackPoint is dividing, create two new daughter TrackPoints properly linked to this one, then call propagate_trackpoint again on each.
        ToDo: Deal with Track ending due to exiting the image frame.
        '''
        print('Propagating track {} at frame {}...'.format(self.trackId, self.frame))
        if self.isLast:
            #Okay to remove the Print statement but not the return statement!
            print('Trackpoint propagation for track {} terminated at frame {}.\n'.format(self.trackId, self.frame))
            return
        nextframe = self.frame + 1
        
        if not self.isDividing:
            self.next_trackpoint = TrackPoint(self.track, nextframe, self)
            self.next_trackpoint.propagate_trackpoint()
        
        if self.isDividing:
            print('Division event for track {} at frame {}!'.format(self.trackId, self.frame))
            print('Propagation continues with daughters {} and {}.\n'.format(self.DaughterA, self.DaughterB))
            self.daughterA_trackpoint = TrackPoint(self.track, nextframe, self, isNewborn = True, newTrackId = self.DaughterA)
            self.daughterB_trackpoint = TrackPoint(self.track, nextframe, self, isNewborn = True, newTrackId = self.DaughterB)
            self.daughterA_trackpoint.propagate_trackpoint()
            self.daughterB_trackpoint.propagate_trackpoint()
    
    def getImage(self, centX = None, centY = None, show = None):
        '''
        Returns (can also display) the ilastik output image at the current TrackPoint's frame, cropped appropriately.
        May need to have TrackPoints also know their labelId (the otherwise useless piece of info) to deal with mergers.
        ToDo: Also show raw fluorescence image.
        '''
        ilastik_image_fpath = self.expt.ilastik_image_fpath
        t = int(self.frame)
        if centX is None:
            centX = self.CentroidX
        if centY is None:
            centY = self.CentroidY
        
        ilastik_stack = io.imread(ilastik_image_fpath)
        [ilastikT,ilastikY,ilastikX] = ilastik_stack.shape
        
        minX = int(max(0,centX-200))
        maxX = int(min(ilastikX,centX+200))
        minY = int(max(0,centY-200))
        maxY = int(min(ilastikY,centY+200))
    
        local_image = ilastik_stack[t,minY:maxY,minX:maxX]
        if show == 'show':
            plt.imshow(local_image)
        return local_image
    
    '''
    @staticmethod
    def simple_stitch(tp1, tp2):
        tp1.next_trackpoint = tp2
        tp2.previous_trackpoint = tp1
    '''
    
    def print_details_through_end(self):
        '''
        Recursive method to print details about this TrackPoint and its linked successors.
        '''
        self.print_trackpoint_details()
        
        if self.next_trackpoint is None and self.daughterA_trackpoint is None and self.daughterB_trackpoint is None:
            return
        
        if self.isDividing:
            self.daughterA_trackpoint.print_details_through_end()
            self.daughterB_trackpoint.print_details_through_end()
        else:
            self.next_trackpoint.print_details_through_end()
            
    def print_trackpoint_details(self):
        '''
        Print some detailed infomation about this TrackPoint.
        '''
        print('\nTrackPoint object from track {} at frame {}.'.format(self.trackId, self.frame))
        if self.isNewborn:
            print('This is a newborn cell.')
        else:
            print('The previous linked trackpoint is {}'.format(str(self.previous_trackpoint)))
        if self.isDividing:
            print('This cell is dividing.')
            print('Daughter A trackpoint is {}'.format(self.daughterA_trackpoint))
            print('Daughter B trackpoint is {}'.format(self.daughterB_trackpoint))
        else:
            print('The next linked trackpoint is {}'.format(str(self.next_trackpoint)))

                    
    def __str__(self):
        return '<<TrackPoint object from track {} at frame {}.>>'.format(self.trackId, self.frame)
    
    __repr__ = __str__
        #Ensures the __str__ output is used whether or not the print() method is explicitly called.