#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 10:37:10 2022

@author: Neelesh
"""

''' Using the PELT search method for optimal changepoint detection'''
#Reading through JSON Data 

#import the json file
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ruptures as rpt
from ruptures.metrics import hausdorff
import time

#Create a sample set of data used to emulate the expected signal of the 
#curvature data
n, dim, sigma = 500, 3, 3 #number of samples, and dimension, standard deviation
n_bkps = 6 #number of change points
signal, bkps = rpt.pw_linear(n, dim, n_bkps, noise_std=sigma)
fig, ax_array = rpt.display(signal, bkps)

penalty_value = 100



algo = rpt.Pelt(model="l2", jump=10, min_size=5).fit(signal)

bkps_python = algo.predict(pen=penalty_value)
print(f"Python PELT Implementation:\t{bkps_python}")
start_time = time.time()
result = algo.predict(pen=penalty_value)

print(f"Python Pelt Implementation:\t{time.time() - start_time:.3f} s")




