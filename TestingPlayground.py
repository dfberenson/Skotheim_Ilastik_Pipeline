# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:16:24 2017

@author: Skotheim Lab
"""
import pandas as pd
import numpy as np

'''
class Test(object):
    
    def __init__(self):
        
        self.ind = np.array([1,2,3,4])
        self.col = np.array([5,6,7,8])
      #  self = self + 2
    
    def add_df(self):
        self.df = pd.DataFrame(0,index = self.ind, columns = self.col)
        
    def plus_one(self):
        self.df = self.df + 2
        
'''
        
        

ind = np.array([1,2,3,4,5])
col = np.array([5,6,7,8])
df = pd.DataFrame(0, index = ind, columns = col)

ind_mini = np.array([2,3])
col_mini = np.array([7])
df_mini = pd.DataFrame(4, index = ind_mini, columns =  col_mini)

df.loc[ind_mini, col_mini] = df_mini
      
     
for i in n.columns:
    print(n.loc[slice(None),i].equals(o.loc[slice(None),i]))

print('Index')
for j in n.index:
    print(n.loc[j].equals(o.loc[j]))