# -*- coding: utf-8 -*-
"""
Created on Tue Nov 07 19:12:50 2017

@author: dfberenson
"""

#Write tools to show how object is moving over time (centroid movement line graph color coded by time?)
#And make trace of intensity and area data


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