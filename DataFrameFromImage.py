# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 13:30:09 2017

@author: dfberenson
"""

class DataFrameFromImages(object):
    
    def __init__(self,expt_name, micrograph_filename = r'E:\Ilastik Tracking\TestImage.tif',
                        tracked_filename = r'E:\Ilastik Tracking\Tracking_Better.tiff'):
        self.expt_name = expt_name
        self.micrograph_filename = micrograph_filename
        self.tracked_filename = tracked_filename
        
    def assign_dataframe(self, known_df):
        self.df = known_df

    def construct_dataframe(self):
        '''
        Creates a dataframe in self.df from the micrograph and tracked filenames.
        The suite of functions that calculate additional data operate on self.df
        '''
        
        start_time = time.clock()
        print('\nLoading images...\n')
        
        #Open two-color microscopy image
        micrograph_stack = io.imread(self.micrograph_filename)
        [T,C,Y,X] = micrograph_stack.shape
        
        #Open grayscale tracked image
        tracked_stack = io.imread(self.tracked_filename)
        [trackedT,trackedY,trackedX] = tracked_stack.shape
        
        #Confirm stack sizes are compatible
        if not (T == trackedT and Y == trackedY and X == trackedX):
            raise ValueError('Stack sizes not matched')
        
        print('\nImages Loaded\n')
        print ('Time elapsed (s): '),
        print (int(time.clock() - start_time))
        
        #Get list of all cells and timepoints
        highest_num_cell = np.max(tracked_stack)
        
        #all_cellnums = np.arange(1,highest_num_cell + 1)    ##ASSUMES CELLS ARE NUMBERED 1,2,3,...,max
        
        all_cellnums = np.unique(tracked_stack)
        all_timepoints = np.arange(0,T)
#        all_timepoints = np.arange(0,4)
        
        
        #Construct multiindexed dataframe where each row is a timepoint and each column
        #is multi-indexed with cell number and measurement type. All values set to nan.
        
        measurements_list = ['Lifespan','Mother','DaughterA','DaughterB','CentroidX','CentroidY',
        'Area','MeanIntensity_Chan1','IntegratedIntensity_Chan1','MeanLocalBackground_Chan1','NetIntegratedIntensity_Chan1',
        'MeanIntensity_Chan2','IntegratedIntensity_Chan2','MeanLocalBackground_Chan2','NetIntegratedIntensity_Chan2']
        
        cellsXmeasurements = pd.MultiIndex.from_product([all_cellnums,measurements_list],
                                                        names = ['cell number','measurement'])
        df = pd.DataFrame(index = all_timepoints, columns = cellsXmeasurements)
        df.index.name = 'frame'
        
        print('\nDataFrame Created\n')
        print ('Time elapsed (s): '),
        print (int(time.clock() - start_time))
        
        def get_mean_local_background(micrograph, tracked_img, x, y):
            #This is very slow. Another option might be to start by running this ~20 times
            #for each timepoint to get a background for 20 different regions of the image
            #and then for each cell just grab the closest one.
            [Y,X] = micrograph.shape
            x1 = int(max(200,x-200))
            x2 = int(min(X-200,x+200))
            y1 = int(max(200,y-200))
            y2 = int(min(Y-200,y+200))
            
            cropped_micrograph = micrograph[y1:y2,x1:x2]
            cropped_tracked_img = tracked_img[y1:y2,x1:x2]
            
            cropped_nocells = (cropped_tracked_img == 0)
            empty_area = np.sum(cropped_nocells)
            empty_integratedintensity = np.sum(cropped_micrograph[cropped_nocells])
            empty_meanintensity = 0
            if not empty_area == 0:
                empty_meanintensity = float(empty_integratedintensity)/empty_area
            
            return empty_meanintensity
        
        
        """
        At each timepoint, go through all cells and get info about them
        Integrated and mean intensities, area, centroid coordinate, etc.
        NB: Mistracked cells may get label 1
        NB: Only works with exactly 2 channels on micrograph
        """
        for t in all_timepoints:
            print('\nMeasuring cells for timepoint ' + str(t) + '\n')
            print ('Time elapsed (s): '),
            print (int(time.clock() - start_time))
        
            this_tracked_img = tracked_stack[t]
            [this_micrograph_Chan1,this_micrograph_Chan2] = micrograph_stack[t]
            
            for cell in all_cellnums:
                #Get Boolean matrix of which pixels correspond to this cell    
                thisimg_currcell = (this_tracked_img == cell)
                
                #Make measurements about the cell
                [centroidY,centroidX] = [0,0]
                if np.any(thisimg_currcell):
                    [centroidY,centroidX] = measure.regionprops(thisimg_currcell.astype(np.int))[0].centroid
                    #measure.regionprops is faster
                
                area = np.sum(thisimg_currcell)
                integratedintensity_Chan1 = np.sum(this_micrograph_Chan1[thisimg_currcell])
                integratedintensity_Chan2 = np.sum(this_micrograph_Chan2[thisimg_currcell])
                if not area == 0:
                    meanintensity_Chan1 = float(integratedintensity_Chan1) / area
                    meanintensity_Chan2 = float(integratedintensity_Chan2) / area
        
                mean_local_background_Chan1 = get_mean_local_background(this_micrograph_Chan1, this_tracked_img, centroidX, centroidY)
                mean_local_background_Chan2 = get_mean_local_background(this_micrograph_Chan2, this_tracked_img, centroidX, centroidY)
        
                #Record measurements into dataframe
                thesemeasurements = df.loc[t,cell]
                thesemeasurements['Lifespan'] = np.nan
                thesemeasurements['Mother'] = np.nan
                thesemeasurements['DaughterA'] = np.nan
                thesemeasurements['DaughterB'] = np.nan
                thesemeasurements['CentroidX'] = centroidX
                thesemeasurements['CentroidY'] = centroidY
                thesemeasurements['Area'] = area
                thesemeasurements['MeanIntensity_Chan1'] = meanintensity_Chan1
                thesemeasurements['IntegratedIntensity_Chan1'] = integratedintensity_Chan1
                thesemeasurements['MeanLocalBackground_Chan1'] = mean_local_background_Chan1
                thesemeasurements['NetIntegratedIntensity_Chan1'] = integratedintensity_Chan1 - mean_local_background_Chan1*area
                thesemeasurements['MeanIntensity_Chan2'] = meanintensity_Chan2
                thesemeasurements['IntegratedIntensity_Chan2'] = integratedintensity_Chan2
                thesemeasurements['MeanLocalBackground_Chan2'] = mean_local_background_Chan2
                thesemeasurements['NetIntegratedIntensity_Chan2'] = integratedintensity_Chan2 - mean_local_background_Chan2*area
                
        print ('\n\nTime for dataframe construction (s): '),
        print (int(time.clock() - start_time))
        df.sort_index(axis = 'columns', inplace = True)
        self.df = df
    
    def smoothen(self,measurement_name,window_radius=2):
        cells = self.df.columns.get_level_values('cell number').unique()
        smooth_name = 'Smoothened ' + measurement_name
        self.add_measurement(smooth_name)
        for cell in cells:
            for t in self.df.index:
                if t < window_radius:
                    self.df.loc[t,(cell,smooth_name)] = self.df.loc[0:t+window_radius,(cell,measurement_name)].mean()
                elif t > max(self.df.index):
                    self.df.loc[t,(cell,smooth_name)] = self.df.loc[t-window_radius:max(self.df.index),(cell,measurement_name)].mean()
                else:
                    self.df.loc[t,(cell,smooth_name)] = self.df.loc[t-window_radius:t+window_radius,(cell,measurement_name)].mean()
                    
    
    def calculate_derivative(self,measurement_name):
        cells = self.df.columns.get_level_values('cell number').unique()
        deriv_name =  'd[' + measurement_name + ']/dt'
        self.add_measurement(deriv_name)
        for cell in cells:
            self.df.loc[0,(cell, deriv_name)] = 0
            for t in self.df.index[1:]:
                val1 = self.df.loc[t-1,(cell,measurement_name)]
                val2 = self.df.loc[t,(cell,measurement_name)]
                self.df.loc[t,(cell,deriv_name)] = val2 - val1
    
    def calculate_relative_derivative(self,measurement_name):
        #Derivative divided by function value, i.e., (dx/dt)/x
        cells = self.df.columns.get_level_values('cell number').unique()
        deriv_name =  'd[' + measurement_name + ']/dt'
        relative_name = 'Relative ' + deriv_name
        self.add_measurement(relative_name)
        for cell in cells:
            for t in self.df.index:
                d = self.df.loc[t,(cell,deriv_name)]
                x = self.df.loc[t,(cell,measurement_name)]
                if x > 0:
                    self.df.loc[t,(cell,relative_name)] = float(d)/x
        
    def calculate_num_neighbors(self,distance):
        name = 'Num neighbors within ' + str(distance) + ' pixels'
        cells = self.df.columns.get_level_values('cell number').unique()
        self.add_measurement(name)
        for cell in cells:
            print('Calculating neighbors for cell ')
            for t in self.df.index:
                home_x = self.df.loc[t,(cell,'CentroidX')]
                home_y = self.df.loc[t,(cell,'CentroidY')]
                neighbor_tally = -1      #So the home cell itself won't be tallied
                for neighbor in cells:
                    neighbor_x = self.df.loc[t,(neighbor,'CentroidX')]
                    neighbor_y = self.df.loc[t,(neighbor,'CentroidY')]
                    if (np.square(neighbor_x - home_x) + np.square(neighbor_y - home_y) <= np.square(distance)):
                        neighbor_tally += 1
                self.df.loc[t,(cell,name)] = neighbor_tally
    
    def calculate_speed(self):
        #This version adds the whole set of Speed columns first
        cells = self.df.columns.get_level_values('cell number').unique()
        self.add_measurement('Speed')
        for cell in cells:
            self.df.loc[0,(cell, 'Speed')] = 0
            for t in self.df.index[1:]:
                x1 = self.df.loc[t-1,(cell,'CentroidX')]
                y1 = self.df.loc[t-1,(cell,'CentroidY')]
                x2 = self.df.loc[t,(cell,'CentroidX')]
                y2 = self.df.loc[t,(cell,'CentroidY')]
                speed = np.sqrt(np.square(x2 - x1) + np.square(y2 - y1))
                self.df.loc[t,(cell, 'Speed')] = speed
    
    def add_measurement(self, measurement_name):
        ind = self.df.index
        cells = self.df.columns.get_level_values('cell number').unique()
        new_df = pd.DataFrame(index = ind, columns = pd.MultiIndex.from_product([cells,[measurement_name]],
                                                                                names = ['cell number','measurement']))
        self.df = self.df.join(new_df)
        self.df.sort_index(axis = 'columns', inplace = True)
    
#    def order_columns(self):
#        self.df = self.df.sort_index(axis = 'columns', level = 'cell number')    
    
    def add_timepoints(self, new_data):
        self.df = self.df.append(new_data)    
    
    def add_empty_timepoint(self):
        cols = self.df.columns
        s = pd.Series(index = cols, name = max(dataframe.index) + 1)
        self.add_timepoints(s)

    def import_stitching_guide(self, stitching_guide):
        #stitching_guide should be a dataframe with one row per timepoint
        #and one column per true track, with values indicating which cellnum
        #in self.df actually matches the proper track
        self.stitching_guide = stitching_guide
    
    def get_stitched_tracks(self):
        measurements = self.df.columns.get_level_values('measurement')
        stitched_tracks = pd.DataFrame(index = self.df.index, columns = pd.MultiIndex.from_product(
                [self.stitching_guide.columns,measurements], names = ['true cell number','measurement']))
        for cell in self.stitching_guide.columns:
            for t in self.df.index:
                orig_cell = self.stitching_guide.loc[t,cell]
                row = self.df.loc[t,orig_cell]
                stitched_tracks.loc[t,cell] = row
        self.stitched_tracks = stitched_tracks
                
        
        stitched_df = pd.DataFrame(self.df.index, self.df.columns)
        for t in self.df.index[init_frames_toskip:]:
            row = self.df.loc[t,cell]
            stitched_df.loc[t] = row
            cell = row.loc['Next stitched ID']
        self.df_unbroken = df_unbroken