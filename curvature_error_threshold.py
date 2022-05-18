#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 10:26:58 2022

@author: Neelesh
"""
"""
The aim of this code is to design a function that will replicate the curvature
error thresholding algortihtm. The code will aim to take the raw curvature 
measurements collected by the FBG sensor, and providing a minimum error the 
algorithm aims to determine the location of forces through detection of the 
breakpoints. Once the location of forces has been determined the data will then
be transferred into the Cosserat Rod model to evaluate the magnitude of force.
 
"""

import numpy as np
import ruptures as rp

def curv_err_thresh(tolerance, num_of_segments,PAF_rail_curvatures):
    """
    Inputs:
    tolerance (float) : predefined error to set as threshold
    
    num_of_segments (int) : User defined max number of segments to iterate over
    In the projects case it is 2, because only 1 point force is being applied,
    so the data should be divided into a list of curvatures
    
    curvatures (list) : list of curvatures measured by the MCF

    Returns:
    force_locations (list) : force locations
    segments () : sequence of interconnected linear curvature segments
    
    Additional requirements:
    The thresholding alogrithm also requires the implementation of a linear
    computational cost function in order to detect the changepoints. In
    Al-Ahmad et Al. 2021 they opted for the PELT method, which has been chosen
    in this project due to the speed/efficiency at which it identifies 
    changepoints.
    """
    #tolerance = 0.05
    #num_of_segments = 2
    
    break_points = []
    segments_matrix = []
    error_vector = []
    #ind_min_error = [] 
    
    #THIS is the implementation of the PELT method by Killick et al. 2012.
    det = rp.Pelt(cost="l2", min_size=1, jump=1)
    data = np.array(PAF_rail_curvatures)

    for i in range(num_of_segments):
        i = i + 1
        break_points = [i, det.find_changepoints(data,1)] #implement linear computational cost function for break_points[i]
        
        
   #THIS IS WHERE I AM UNSURE ABOUT WHAT TO DO NEXT     
        segments_matrix = create_segs_fun[break_points, curvatures]
        error_vector = curvatures - segments_matrix ###ensure these are the same dimensions### 
        if error_vector < tolerance:
            return (len(break_points))
            print (len(break_points))
        else:
            error_vector = error_vector
        #ind_min_error = ?
        
        #force_locations = break_points 
        print(error_vector)
        #return force_locations, segments