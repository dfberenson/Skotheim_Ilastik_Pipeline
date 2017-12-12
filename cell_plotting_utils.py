# -*- coding: utf-8 -*-
"""
Created on Tue Nov 07 19:12:50 2017

@author: dfberenson
"""

#Write tools to show how object is moving over time (centroid movement line graph color coded by time?)
#And make trace of intensity and area data


def show_stack_with_slider(im_stack):

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider
    
    ax = plt.subplot(1,1,1)
    plt.subplots_adjust(left = 0.25, bottom = 0.25)
    
    frame = 0
    img = plt.imshow(im_stack[frame,:,:])
    axframe = plt.axes([0.25,0.1,0.6,0.05])
    slider_frame = Slider(axframe, 'Frame', 0, len(im_stack), valinit = 0)
    
    def update(val):
        frame = np.around(slider_frame.val)
        img.set_data(im_stack[frame,:,:])
    
    slider_frame.on_changed(update)
    plt.show()

def plot_average_value(dataframe, measurement_name):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    times = dataframe.index
    vals = dataframe.xs(measurement_name, level='measurement', axis=1)
    avg_vals = pd.Series(index = times)
    for t in times:
        avg_vals.loc[t] = np.mean(vals.loc[t,2:])       #Skip cells numbered 0 and 1 (artifacts)

    plt.figure()
    plt.plot(times,avg_vals)
    plt.show()

def plot_track_centroid_motion(cellnum, dataframe, xlim = 2560, ylim = 2160):
    #cellnum is int so only one cell
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    times = dataframe.index
    xcoords = dataframe.xs((cellnum,'CentroidX'), level=('cell number','measurement'), axis='columns')
    ycoords = dataframe.xs((cellnum,'CentroidY'), level=('cell number','measurement'), axis='columns')
    
    #With sorted dataframe.index, can also do:
        # measurement_timecourse = dataframe.loc[slice(None),(track,measurement)]
    
    plt.figure()
    plt.axis([0,xlim,0,ylim])
    plt.plot(xcoords,ycoords)
    plt.gca().invert_yaxis()
    
    plt.figure()
    plt.axis([0,xlim,0,ylim])
    plt.scatter(xcoords,ycoords, c=times)
    plt.gca().invert_yaxis()
    
def plot_tracks_centroids_motions(cellnums, dataframe, xlim = 2560, ylim = 2160):
    #cellnums is list so multiple cells
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    xcoords = [None] * len(cellnums)
    ycoords = [None] * len(cellnums)
    
    for n in range(len(cellnums)):
        times = dataframe.index
        xcoords[n] = dataframe.xs((cellnums[n],'CentroidX'), level=('cell number','measurement'), axis='columns')
        ycoords[n] = dataframe.xs((cellnums[n],'CentroidY'), level=('cell number','measurement'), axis='columns')
    
    #With sorted dataframe.index, can also do:
        # measurement_timecourse = dataframe.loc[slice(None),(track,measurement)]
    
    plt.figure()
    plt.axis([0,xlim,0,ylim])
    for n in range(len(cellnums)):
        plt.plot(xcoords[n],ycoords[n])
    plt.gca().invert_yaxis()
    
    plt.figure()
    plt.axis([0,xlim,0,ylim])
    for n in range(len(cellnums)):
        plt.scatter(xcoords[n],ycoords[n], c=times)
    plt.gca().invert_yaxis()
    
def plot_intensity(cellnum, dataframe, ylim = None):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    times = dataframe.index
    intens_Chan1 = dataframe.xs((cellnum,'IntegratedIntensity_Chan1'), level=('cell number','measurement'), axis=1)
    intens_Chan2 = dataframe.xs((cellnum,'IntegratedIntensity_Chan2'), level=('cell number','measurement'), axis=1)
    
    plt.figure()
    axes = plt.gca()
    axes.plot(times,intens_Chan1,'r-')
    axes.set_xlabel('Frame')
    axes.set_ylabel('IntegratedIntensity_Chan1',color='r')
    axes.tick_params('y', colors='r')
    axes2 = axes.twinx()
    axes2.plot(times,intens_Chan2,'g-')
    axes2.set_ylabel('IntegratedIntensity_Chan2',color='g')
    axes2.tick_params('y', colors='g')

    plt.show()


def plot_variable(cellnum, dataframe, measurement_name):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    times = dataframe.index
    vals = dataframe.xs((cellnum, measurement_name), level=('cell number','measurement'), axis=1)

    plt.figure()
    plt.plot(times,vals)
    plt.show()
    
    
def compare_area_with_intensity(dataframe):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    areas = dataframe.xs('Area', level = 'measurement', axis=1).values.flatten()
    intens_Chan1 = dataframe.xs('IntegratedIntensity_Chan1', level = 'measurement', axis=1).values.flatten()
    intens_Chan2 = dataframe.xs('IntegratedIntensity_Chan2', level = 'measurement', axis=1).values.flatten()
    
    plt.figure()
    plt.scatter(areas,intens_Chan1,color='r')
    plt.scatter(areas,intens_Chan2,color='g')
    plt.show()