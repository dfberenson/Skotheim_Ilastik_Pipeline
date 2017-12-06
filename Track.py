# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 18:52:38 2017

@author: dfberenson
"""

class Track(object):
    
    def __init__(self, df, trackId, init_frame):
        
        self.df = df
        self.trackId = trackId
        self.init_frame = init_frame
        
        self.init_trackpoint = TrackPoint(self, self.init_frame, None)
        
        self.init_trackpoint.propagate_trackpoint()




track= Track(df, 5, 0)
track.init_trackpoint.print_details_through_end()