# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 19:27:46 2017

@author: dfberenson
"""

    
import matplotlib.pyplot as plt
import numpy as np
    

class TrackGui(object):
    '''
    A TrackGui object is created to handle viewing and interacting with cell tracks in a very local area (in time and space).
    The parameter i indicates which frame to display and is always used as modulo self.im_length so the stack can be cycled through.
    The matplotlib.pyplot figure listens for keyboard and mouse input and responds appropriately.
    ToDo: Make the clicks actually *do* something other than just print information.
    '''

    def __init__(self, expt, tracknum, first_frame, stack_length):
        '''
        Displays the first frame of the mini image stack, then connects to the keyboard and mouse.
        '''
        TrackGui.printInstructions()
        
        self.expt = expt
        self.tracknum = tracknum
        self.first_frame = first_frame
        self.stack_length = stack_length
        
        self.thistrack = self.expt.tracks_list[self.tracknum]
        self.im_stack, self.trackpoint_stack = self.thistrack.getImStack_and_TrackPointStack(self.first_frame, self.stack_length)
            #Only the self.im_stack output is actually used.
        
        self.im_length = len(self.im_stack)
        self.i = 0
        
        self.fig,self.ax = plt.subplots()
        self.ax.imshow(self.im_stack[self.i])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        self.connect()
        
        
    def connect(self):
        '''
        Tells the figure canvas to listen for the appropriate events.
        '''
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidscroll = self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.cidkey = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self,event):
        '''
        Move through time using 'a' and 'd' keys.
        '''
        if event.key == 'd':
            self.i += 1        
        elif event.key == 'a':
            self.i -= 1
        plt.cla()
        self.ax.imshow(self.im_stack[self.i % self.im_length])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        plt.draw()

    def on_scroll(self,event):
        '''
        Move through time by scrolling mouse wheel.
        '''
        if event.button == 'down':
            self.i += 1        
        elif event.button == 'up':
            self.i -= 1
        plt.cla()
        self.ax.imshow(self.im_stack[self.i % self.im_length])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        plt.draw()

    def on_press(self, event):
        '''
        On left click: print the TrackPoints corresponding to the clicked cell.
        On right click: set the clicked cell's value to 1 and all other cells to 0.
        '''
        
#        print('you pressed', event.button, event.xdata, event.ydata)    
        if event.button == 1:
            print('Found the following trackpoints corresponding to your click:')
            matching_tps = self.getClickedTrackPoints(int(event.xdata),int(event.ydata))
            for tp in matching_tps:
                print(tp)
        
        elif event.button == 3:
            x,y = int(event.xdata), int(event.ydata)
            curr_img = self.im_stack[self.i % self.im_length]
            curr_val = curr_img[y,x]
            print(x,y,curr_val)
            if curr_val != 0:
                curr_img_clickedcell = (curr_img == curr_val).astype('uint32')
                self.im_stack[self.i % self.im_length] = curr_img_clickedcell
        
        plt.cla()
        self.ax.imshow(self.im_stack[self.i % self.im_length])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        plt.draw()
        
    def getClickedTrackPoints(self,x,y):
        '''
        Using x- and y-coordinates of the click, find the lineage of the selected cell.
        Then find the TrackPoints matching the current frame and selected lineage, using the Experiment.getMatchingTrackpoints method.        
        TBD: Compare based on labelId rather than lineageId.
        '''
        frame = self.i % self.im_length
        lineage = self.im_stack[frame,y,x]   #Should perhaps become LabelId as part of larger overhaul
        matching_tps = self.expt.getMatchingTrackpoints(frame = frame, lineage = lineage)
        return matching_tps
    
    @staticmethod
    def printInstructions():
        print('\n\n\n\n\n')
        print('Scroll to travel through stack.')
        print('Right-click cell to label it.')
