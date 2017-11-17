# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:12:52 2017

@author: dfberenson
"""

"""
Introduce Manual Track

Read x,y data from FIJI manual track
Load "Tracked Cell X" image, where X = some number
Go through image, converting pixels whose value matches the value at [x,y] to X

Then can use this image through the main pipeline
"""

def relabelManualTrack(tracked_stack_filename = r'E:\Ilastik Tracking\TinyTrack.tif',
                       newcellnum = 2000):

    from skimage import io
    import pandas as pd
    import numpy as np
    
    tracked_stack = io.imread(tracked_stack_filename)
    tracked_stack = np.float32(tracked_stack)
    [trackedT,trackedY,trackedX] = tracked_stack.shape
    
    folder = r'E:\Ilastik Tracking'
    track_xlsx_name = 'Cell{}_ManualTrack.xlsx'.format(newcellnum)
    track_xlsx_path = folder + '\\' + track_xlsx_name
    
    if tracked_stack_filename[-5:0] == '.tiff':
        relabeled_stack_path = tracked_stack_filename[:-5] + '_Cell' + str(newcellnum) + '.tiff'
    elif tracked_stack_filename[-4:0] == '.tif':
        relabeled_stack_path = tracked_stack_filename[:-4] + '_Cell' + str(newcellnum) + '.tif'
    else:               
        relabeled_stack_path = r'E:\Ilastik Tracking\Relabeled_Cell{}.tif'.format(newcellnum)
    
    track_df = pd.read_excel(track_xlsx_path)
    
    for t in np.arange(0,trackedT):
        
        x = np.int(track_df.loc[t,'X'])
        y = np.int(track_df.loc[t,'Y'])
        tracked_thisframe = tracked_stack[t]
        orig_px_val = tracked_thisframe[y,x]   
        tracked_thisframe[tracked_thisframe == orig_px_val] = np.float(newcellnum)
        tracked_stack[t] = tracked_thisframe
                     
    io.imsave(relabeled_stack_path, tracked_stack)
    return relabeled_stack_path