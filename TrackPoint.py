# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 19:01:23 2017

@author: dfberenson
"""


class TrackPoint(object):
    
    def __init__(self, track, frame, previous_trackpoint, isNewborn = False, newTrackId = None):
        '''
        Creates a TrackPoint object corresponding to a single tracked object at a single timepoint.
        Arguments:
            track = Track object to which this TrackPoint object belongs
            frame = int corresponding to the timepoint that can be looked up in the dataframe
            previous_trackpoint = TrackPoint object for the same Tracked cell in the previous timepoint
        '''
        self.track = track
        self.frame = frame
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
        
        df = track.df
                
        self.Lineage = df.loc[frame,(self.trackId,'Lineage')]
        self.Mother = df.loc[frame,(self.trackId,'Mother')]
        self.DaughterA = df.loc[frame,(self.trackId,'DaughterA')]
        self.DaughterB = df.loc[frame,(self.trackId,'DaughterB')]
        if not np.isnan(self.DaughterA) or not np.isnan(self.DaughterB):
            self.isDividing = True
        
        self.Area = df.loc[frame, (self.trackId,'Area')]
        self.MeanIntensity_Chan1 = df.loc[frame ,(self.trackId,'MeanIntensity_Chan1')]
        self.MeanIntensity_Chan2 = df.loc[frame ,(self.trackId,'MeanIntensity_Chan2')]
        self.CentroidX = df.loc[frame ,(self.trackId,'CentroidX')]
        self.CentroidY = df.loc[frame ,(self.trackId,'CentroidY')]
   

    def propagate_trackpoint(self):
        
        nextframe = self.frame + 1
        if nextframe > max(self.track.df.index):
            print('Trackpoint propagation for track {} terminated at frame {}'.format(self.trackId, self.frame))
            return
        
        if not self.isDividing:
            self.next_trackpoint = TrackPoint(self.track, nextframe, self)
            self.next_trackpoint.propagate_trackpoint()
        
        if self.isDividing:
            self.daughterA_trackpoint = TrackPoint(self.track, nextframe, self, isNewborn = True, newTrackId = self.DaughterA)
            self.daughterB_trackpoint = TrackPoint(self.track, nextframe, self, isNewborn = True, newTrackId = self.DaughterB)
            self.daughterA_trackpoint.propagate_trackpoint()
            self.daughterB_trackpoint.propagate_trackpoint()
    
    @staticmethod
    def simple_stitch(tp1, tp2):
        tp1.next_trackpoint = tp2
        tp2.previous_trackpoint = tp1
    
    
    def print_details_through_end(self):
        self.print_trackpoint_details()
        
        if self.next_trackpoint is None and self.daughterA_trackpoint is None and self.daughterB_trackpoint is None:
            return
        
        if self.isDividing:
            self.daughterA_trackpoint.print_details_through_end()
            self.daughterB_trackpoint.print_details_through_end()
        else:
            self.next_trackpoint.print_details_through_end()
        
                
    def __str__(self):
        return 'TrackPoint object from track {} at frame {}.'.format(self.trackId, self.frame)
            
    def print_trackpoint_details(self):
        print('\nTrackPoint object from track {} at frame {}.'.format(self.trackId, self.frame))
        if self.isNewborn:
            print('This is a newborn cell.')
        else:
            print('The previous linked trackpoint is {}'.format(str(self.previous_trackpoint)))
        if self.isDividing:
            print('This cell is dividing.')
            print('Daughter A trackpoint is {}.'.format(self.daughterA_trackpoint))
            print('Daughter B trackpoint is {}.'.format(self.daughterB_trackpoint))
        else:
            print('The next linked trackpoint is {}.'.format(str(self.next_trackpoint)))
