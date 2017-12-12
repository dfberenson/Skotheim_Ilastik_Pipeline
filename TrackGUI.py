# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 19:27:46 2017

@author: dfberenson
"""

    
import matplotlib.pyplot as plt
import numpy as np
    

class TrackGui(object):

    def __init__(self, expt, tracknum, first_frame, stack_length):
        
        TrackGui.printInstructions()
        
        self.expt = expt
        self.tracknum = tracknum
        self.first_frame = first_frame
        self.stack_length = stack_length
        
        self.thistrack = self.expt.tracks_list[self.tracknum]
        self.im_stack, self.trackpoint_stack = self.thistrack.getImStack_and_TrackPointStack(self.first_frame, self.stack_length)
        
        self.im_length = len(self.im_stack)
        self.i = 0
        
        self.fig,self.ax = plt.subplots()
        self.ax.imshow(self.im_stack[self.i])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        self.connect()
        
        
    def connect(self):
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidscroll = self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.cidkey = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self,event):
        if event.key == 'd':
            self.i += 1        
        elif event.key == 'a':
            self.i -= 1
        plt.cla()
        self.ax.imshow(self.im_stack[self.i % self.im_length])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        plt.draw()

    def on_scroll(self,event):
        if event.button == 'down':
            self.i += 1        
        elif event.button == 'up':
            self.i -= 1
        plt.cla()
        self.ax.imshow(self.im_stack[self.i % self.im_length])
        plt.title('{}/{}'.format(self.i % self.im_length,self.im_length-1), loc='right')
        plt.draw()

    def on_press(self, event):
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
        frame = self.i % self.im_length
        lineage = self.im_stack[frame,y,x]   #Should perhaps become LabelId as part of larger overhaul
        matching_tps = self.expt.getMatchingTrackpoints(frame = frame, lineage = lineage)
        return matching_tps
    
    @staticmethod
    def printInstructions():
        print('\n\n\n\n\n')
        print('Scroll to travel through stack.')
        print('Right-click cell to label it.')
    
        
#g = TrackGui(im_stack)

'''
import matplotlib.pyplot as plt
import numpy as np

#im_stack = np.array([np.array([[1,2],[3,4]]),np.array([[8,7],[6,5]])])
frames = len(im_stack)

def on_press(event):
    print('you pressed', event.button, event.xdata, event.ydata)
    global x
    x = x + 1
    plt.cla()
    ax.imshow(im_stack[x%frames])
    plt.draw()

fig,ax = plt.subplots()
x = 0
ax.imshow(im_stack[x])
cid = fig.canvas.mpl_connect('button_press_event', on_press)
plt.draw()
'''
