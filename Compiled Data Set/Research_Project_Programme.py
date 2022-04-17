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
#import math

#Opening the json file:
folder = "/Users/Neelesh/Desktop/Coding Files/Compiled Data Set/"
force_string = ["Dynamometer_", "0.5N_","1N_","1.5N_","2N_","2.5N_"]
run_string = ["run1","run2","run3","run4","run5"]

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

        plt.plot(curvatures[10:18], linestyle = "-.")
        plt.xlabel('arc length')
        plt.ylabel('curvature')
        plt.legend(run_string)
        plt.ylim((-0.5,0.5));    
    
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

curvatures_1 = curvature_series[15]

#Employing the PELT method with changepoint detection from Killick et Al.
#RUPTURES PACKAGE#

def PELT(curvatures_1[10:18]):
    
#model = "rbf"
#algo = pelt(model=model).fit(curvatures_1[10:18])
#result = algo.predict(pen=10)
#plt.title('Change Point Detection: Pelt Search Method')
#display = (curvatures[10:18], result)
#plt.show()  
 

#Employing the Cosserat Rod Model on the curvature data





def curv_err_thres(tolerance,num_of_segments_max,curvatures):
    """
    Inputs:
    tolerance (float) : predefined error to set as threshold
    num_of_segments (int) : max number of segments to iterate over 
    curvatures (list) : list of curvatures

    Returns:
    force_locations (list) : force locations
    segments () : sequence of interconnected linear curvature segments
    """
    tolerance = 0.05
    num_of_segments = 25
    break_points = []
    segments_matrix = []
    error_vector = []
    #ind_min_error = [] 

    for i in range(num_of_segments):
        i = i + 1
        break_points[i] = [i, curv_core1]
        #implement linear computational cost function for break_points[i] using PELT method from Killick et Al. 2012
        segments_matrix = create_segs_fun[break_points, curvature_series[x]]
        error_vector = curvature_series[x] - segments_matrix ###ensure these are the same dimensions### 
        if error_vector < tolerance:
            return (len(break_points))
            print (len(break_points))
        else:
            error_vector = error_vector
        #ind_min_error = ?
        #force_locations = break_points 
        print(error_vector)
        #return force_locations, segments
        








#2) Insert an equation that converts the delta_strain measurements to force 
#measurements and iterates through the entire data set. Create a separate 
#numpy array of force data where it is plotted against change in curvature. 

i = (2, 4, 6) #Numbers required to convert multiples of 120 degrees to radians
def strain(curvature_series, r=0.0038, bend_angle=(np.pi), ith_core_angle= i[0] * np.pi/3):
    """
    Writing my own python function to convert wav_data series into changes in 
    curvature. Once converted into curvature convert into strain measurements,
    which gives the force.
    

    Defining the input parameters
    ----------
    delta_strain[X] : TYPE: NUMPY array. It is the numpy array of all calculated 
    changes in wavelength (nm) by the FBG sensor outer cores.
    
    r : TYPE: Distance in cm. The distance of the outer cores to the central core 
    of the MCF. The default is 0.0038cm.
    
    bend_angle : TYPE: An angle in radians. It is defined as the angle between 
    the x-axis and the curvature vector.
    
    ith_core_angle : TYPE: An angle in radians, It is the angle of the ith core.
    It is in multiples of 2*pi/3.

    Returns a list of strain measurements, which shows how changes in curvature 
    cause a change in force along the MCF.
    -------
    TYPE: Should be a numpy array?
    The array should be a list of values that can then be plotted to show 
    changes in force and then compared with algorithms to detect which method is 
    best at replicating the raw experimental data.

    """
    

    


#3) Apply an algorithm that can best estimate the raw force data most accurately. 
#Maximum of 1/2 algorithms chosen.






#4) Finally if the force exceeds a certain threshold I want the programme to have a 
#warning set up to alert the user of this (Could be on the plot?).













    






