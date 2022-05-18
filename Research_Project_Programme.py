#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 12:29:15 2022

@author: Neelesh
"""

#Reading through JSON Data 

#import the json file
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from curvature_error_threshold import curv_err_thresh
import ruptures as rpt
from ruptures.metrics import hausdorff
import time

#Opening the json file:
folder = "/Users/Neelesh/Desktop/Coding Files/Compiled Data Set/" #Ensure your folder string is appropriate for your computer

force_string = ["Dynamometer_", "0.5N_","1N_","1.5N_","2N_","2.5N_"] #Different masses used

run_string = ["run1","run2","run3","run4","run5"] #Number of repetitions for each mass completed



#This figure aims to plot the raw curvature wavelengths detected by the MCF, as 
#well as demonstrate where the load is placed on the PAF rail with the use of a 
#vertical line.

plt.figure(figsize=(20,10))
for force_ind in range(len(force_string)):
    plt.subplot(2,3,force_ind+1)
    plt.title(force_string[force_ind])
    for run in run_string:

        file = folder + force_string[force_ind] + run + ".json"

        with open(file,"r") as json_file:
            data = json.load(json_file)

        exp_params = data["experiment_parameters"]
        data = data["data"]

        curvatures = data[0]['curvatures']
        PAF_rail_curvatures = curvatures[10:19]

        plt.plot(PAF_rail_curvatures, linestyle = "-.")
        plt.xlabel('arc length')
        plt.ylabel('curvature')
        plt.legend(run_string, loc = "upper right")
        plt.xlim(0,8)
        plt.ylim((-0.2,0.2)); 
        plt.axvline(x = 4, color="black")


#Calling the curvature error thresholding algorithm
#curv_err_thresh(tolerance=0.05, num_of_segments=2, PAF_rail_curvatures = PAF_rail_curvatures )



    
with open('2.5N_run3.json') as json_data:
    #print(type(json_data))
    experiment_data = json.load(json_data)

#for reference_wavelengths in experiment_data['experiment_parameters']['wav0']:
#   ref_wav = reference_wavelengths

df = pd.DataFrame.from_dict(experiment_data.get('data'), orient='columns')  

df1 = pd.DataFrame.from_dict(experiment_data.get('experiment_parameters'), orient='columns')  

##Obtaining reference wavelengths from the dataframe in a numpy array format
reference_wavelengths = df1['wav0'].apply(lambda x:np.array(x)).to_numpy()

#Obtaining curvatures from the dataframe in a numpy array format
curvature_series = df['curvatures'].apply(lambda x:np.array(x)).to_numpy()

#Obtaining wave data from the data frame in a numpy array format
wav_data = df['wav_data'].apply(lambda x:np.array(x)).to_numpy()

#Obtaining 2D position data  from the dataframe in a numpy array format
positions_2d = df['positions_3d'].apply(lambda x:np.array(x)).to_numpy()

#Obtaining 3D position data from the dataframe in a numpy array format
positions_3d = df['positions_3d'].apply(lambda x:np.array(x)).to_numpy()

signal = curvature_series

algo_python = rpt.Pelt(model="rbf", jump=1, min_size=2).fit(
    signal
)  # written in pure python
penalty_value = 1

for (label, algo) in zip(
    ("Python implementation"), (algo_python)
):
    start_time = time.time()
    result = algo.predict(pen=penalty_value)
    print(f"{label}:\t{time.time() - start_time:.3f} s")

        






















    






