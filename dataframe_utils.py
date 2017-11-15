# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:31:04 2017

@author: dfberenson
"""
'''
These functions have become methods for TrackingDataFrame
'''

def calculate_derivative(dataframe,measurement_name):
    cells = dataframe.columns.get_level_values('cell number').unique()
    deriv_name =  'd[' + measurement_name + ']/dt'
    dataframe = add_measurement(dataframe, deriv_name)
    for cell in cells:
        dataframe.loc[0,(cell, deriv_name)] = 0
        for t in dataframe.index[1:]:
            val1 = dataframe.loc[t-1,(cell,measurement_name)]
            val2 = dataframe.loc[t,(cell,measurement_name)]
            dataframe.loc[t,(cell,deriv_name)] = val2 - val1
    return dataframe
    
def calculate_relative_derivative(dataframe,measurement_name):
    #Derivative divided by function value, i.e., (dx/dt)/x
    cells = dataframe.columns.get_level_values('cell number').unique()
    deriv_name =  'd[' + measurement_name + ']/dt'
    relative_name = 'Relative ' + deriv_name
    dataframe = add_measurement(dataframe,relative_name)
    for cell in cells:
        for t in dataframe.index:
            d = dataframe.loc[t,(cell,deriv_name)]
            x = dataframe.loc[t,(cell,measurement_name)]
            if x > 0:
                dataframe.loc[t,(cell,relative_name)] = float(d)/x
    return dataframe
    
def calculate_num_neighbors(dataframe,distance):
    name = 'Num neighbors within' + str(distance) + 'pixels'
    cells = dataframe.columns.get_level_values('cell number').unique()
    dataframe = add_measurement(dataframe,name)
    for cell in cells:
        for t in dataframe.index:
            home_x = dataframe.loc[t,(cell,'CentroidX')]
            home_y = dataframe.loc[t,(cell,'CentroidY')]
            neighbor_tally = -1      #So the home cell itself won't be tallied
            for neighbor in cells:
                neighbor_x = dataframe.loc[t,(neighbor,'CentroidX')]
                neighbor_y = dataframe.loc[t,(neighbor,'CentroidY')]
                if (np.square(neighbor_x - home_x) + np.square(neighbor_y - home_y) <= np.square(distance)):
                    neighbor_tally += 1
            dataframe.loc[t,(cell,name)] = neighbor_tally
    return dataframe

def calculate_speed(dataframe):
    #This version adds the whole set of Speed columns first
    cells = dataframe.columns.get_level_values('cell number').unique()
    dataframe = add_measurement(dataframe, 'Speed')
    for cell in cells:
        dataframe.loc[0,(cell, 'Speed')] = 0
        for t in dataframe.index[1:]:
            x1 = dataframe.loc[t-1,(cell,'CentroidX')]
            y1 = dataframe.loc[t-1,(cell,'CentroidY')]
            x2 = dataframe.loc[t,(cell,'CentroidX')]
            y2 = dataframe.loc[t,(cell,'CentroidY')]
            speed = np.sqrt(np.square(x2 - x1) + np.square(y2 - y1))
            dataframe.loc[t,(cell, 'Speed')] = speed
    return dataframe

def add_measurement(dataframe, measurement_name):
    ind = dataframe.index
    cells = dataframe.columns.get_level_values('cell number').unique()
    new_df = pd.DataFrame(index = ind, columns = pd.MultiIndex.from_product([cells,[measurement_name]],
                                                                            names = ['cell number','measurement']))
    dataframe = dataframe.join(new_df)
    dataframe = order_columns(dataframe)
    return dataframe



def order_columns(dataframe):
    dataframe = dataframe.sort_index(axis = 'columns', level = 'cell number')
    return dataframe


def add_timepoints(dataframe, new_data):
    dataframe = dataframe.append(new_data)
    return dataframe


def add_empty_timepoint(dataframe):
    cols = dataframe.columns
    s = pd.Series(index = cols, name = max(dataframe.index) + 1)
    dataframe = add_timepoints(dataframe, s)
    return dataframe


#def calculate_speed_slow(dataframe):
#    start_time = time.clock()
#    cells = dataframe.columns.get_level_values('cell number').unique()
#    for cell in cells:
#        dataframe = add_measurement_onecell(dataframe, cell, 'Speed3')
#        #Perhaps can speed this up by adding all the new Speed colums at once
#        #To avoid constant memory reallocation
#        dataframe.loc[0,(cell, 'Speed3')] = 0
#        for t in dataframe.index[1:]:
#            x1 = dataframe.loc[t-1,(cell,'CentroidX')]
#            y1 = dataframe.loc[t-1,(cell,'CentroidY')]
#            x2 = dataframe.loc[t,(cell,'CentroidX')]
#            y2 = dataframe.loc[t,(cell,'CentroidY')]
#            speed = np.sqrt(np.square(x2 - x1) + np.square(y2 - y1))
#            dataframe.loc[t,(cell, 'Speed3')] = speed
#    print(time.clock() - start_time)
#    return dataframe


#def add_measurement_onecell(dataframe, cellnum, measurement_name):
#    #Adds column for chosen measurement for the chosen cell
#    #Column is filled with NaN
#    s = pd.Series(index = dataframe.index)
#    dataframe[cellnum,measurement_name] = s
#    return dataframe
