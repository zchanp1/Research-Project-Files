#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:14:34 2022

@author: Neelesh
"""
"""
GETTING STARTED WITH PyElastica:
The aim of this code is to design a system based on the Timoshenko_Beam Case to 
see if it can accurtately represent/estimate the case for estimating loading 
forces on an FBG sensor.    
"""


import numpy as np
import sys
import matplotlib.pyplot as plt

# FIXME without appending sys.path make it more generic
sys.path.append("../../")

#Import Wrappers,
from elastica.wrappers import BaseSystemCollection, Constraints, Forcing

#Import Cosserat Rod Class
from elastica.rod.cosserat_rod import CosseratRod

#Import Boundary Condition Classes
from elastica.boundary_conditions import OneEndFixedBC
from elastica.external_forces import EndpointForces

#Import Timestepping Functions
from elastica.timestepper.symplectic_steppers import PositionVerlet
from elastica.timestepper import integrate
#from elastica.TimoshenkoBeamCase.timoshenko_postprocessing import plot_timoshenko


class TimoshenkoBeamSimulator(BaseSystemCollection, Constraints, Forcing):
    pass


timoshenko_sim = TimoshenkoBeamSimulator()
final_time = 3000 #time in ms
# Options
PLOT_FIGURE = True
SAVE_FIGURE = False
SAVE_RESULTS = False
ADD_UNSHEARABLE_ROD = True

# setting up test params
n_elem = 25
start = np.zeros((3,))
direction = np.array([0.0, 0.0, 1.0])
normal = np.array([0.0, 1.0, 0.0])
base_length = 250 #length in mm
base_radius = 3.7e-3 #length in mm
base_area = np.pi * base_radius ** 2
density = 5000
nu = 0.1
E = 1e15
# For shear modulus of 1e4, nu is 99!
poisson_ratio = 999
shear_modulus = E / (poisson_ratio + 1.0)

shearable_rod = CosseratRod.straight_rod(
    n_elem,
    start,
    direction,
    normal,
    base_length,
    base_radius,
    density,
    nu,
    E,
    shear_modulus=shear_modulus,
)

timoshenko_sim.append(shearable_rod)


#Adding Boundary Conditions
'''
We need to ensure that one end of the rod is fixed, and we are aiming to 
constrain the shearable_rod object using the OneEndFixedRod type of constraint.

We also need to define which node of the rod is being constrained. In our case
because the FBG sensor has 9 gratings in the PAF rail and it is placed in 
ranges from 11-18, we are going to constrain it at the beginning, leaving it 
free at one end. 
'''
timoshenko_sim.constrain(shearable_rod).using(
    OneEndFixedBC, constrained_position_idx=(0,), constrained_director_idx=(0,)
)


'''
The next boundary condition that needs to be applied is the the endpoint force.
Similar to how the we constrained the system we want the the timoshenko_sim
simulator to add_forcing_to the shearable_rod object using the EndpointForces 
type of forcing. This EndpointForces applies force to both ends of the rod. 
However, we want to apply force at only one specific end of the rod, so we do 
this by specifying the force vector to be applied at each end: origin_force and 
end_force. Eventually I would want to know if it is possible to apply force to 
the middle of the rod. This has not been achieved yet ut I would like to see 
if it is possible to change the location of the force to the middle obf the 
rail.
'''
end_force = np.array([-2.5, 0.0, 0.0])
timoshenko_sim.add_forcing_to(shearable_rod).using(
    EndpointForces, 0.0 * end_force, end_force, ramp_up_time=final_time / 2.0
)


#ADD UNSHEARABLE ROD FOR COMPARISON
'''
The unshearable rod is created to compare with the shearable rod, and provide 
a comparison with an ideal case, to see how well this method can approximate 
using the Cosserat Rod theory.
'''

if ADD_UNSHEARABLE_ROD:
    # Start into the plane
    unshearable_start = np.array([0.0, -1.0, 0.0])
    shear_modulus = E / (-0.7 + 1.0)
    unshearable_rod = CosseratRod.straight_rod(
        n_elem,
        unshearable_start,
        direction,
        normal,
        base_length,
        base_radius,
        density,
        nu,
        E,
        # Unshearable rod needs G -> inf, which is achievable with -ve poisson ratio
        shear_modulus=shear_modulus,
    )

    timoshenko_sim.append(unshearable_rod)
    timoshenko_sim.constrain(unshearable_rod).using(
        OneEndFixedBC, constrained_position_idx=(0,), constrained_director_idx=(0,)
    )
    timoshenko_sim.add_forcing_to(unshearable_rod).using(
        EndpointForces, 0.0 * end_force, end_force, ramp_up_time=final_time / 2.0
    )

timoshenko_sim.finalize()
timestepper = PositionVerlet()
# timestepper = PEFRL()

dl = base_length / n_elem
dt = 0.01 * dl
total_steps = int(final_time / dt)
print("Total steps", total_steps)
integrate(timestepper, timoshenko_sim, final_time, total_steps)

#Time to run the simulation
integrate(timestepper, timoshenko_sim, final_time, total_steps)

# Compute beam position for sherable and unsherable beams.
def analytical_result(arg_rod, arg_end_force, shearing=True, n_elem=500):
    base_length = np.sum(arg_rod.rest_lengths)
    arg_s = np.linspace(0.0, base_length, n_elem)
    if type(arg_end_force) is np.ndarray:
        acting_force = arg_end_force[np.nonzero(arg_end_force)]
    else:
        acting_force = arg_end_force
    acting_force = np.abs(acting_force)
    linear_prefactor = -acting_force / arg_rod.shear_matrix[0, 0, 0]
    quadratic_prefactor = (
        -acting_force
        / 2.0
        * np.sum(arg_rod.rest_lengths / arg_rod.bend_matrix[0, 0, 0])
    )
    cubic_prefactor = (acting_force / 6.0) / arg_rod.bend_matrix[0, 0, 0]
    if shearing:
        return (
            arg_s,
            arg_s * linear_prefactor
            + arg_s ** 2 * quadratic_prefactor
            + arg_s ** 3 * cubic_prefactor,
        )
    else:
        return arg_s, arg_s ** 2 * quadratic_prefactor + arg_s ** 3 * cubic_prefactor
    
if PLOT_FIGURE:
    def plot_timoshenko(shearable_rod, unshearable_rod, end_force):
        

        analytical_shearable_positon = analytical_result(
            shearable_rod, end_force, shearing=True
        )
        analytical_unshearable_positon = analytical_result(
            unshearable_rod, end_force, shearing=False
        )

        fig = plt.figure(figsize=(5, 4), frameon=True, dpi=150)
        ax = fig.add_subplot(111)
        ax.grid(visible=True, which="major", color="grey", linestyle="-", linewidth=0.25)

        ax.plot(
            analytical_shearable_positon[0],
            analytical_shearable_positon[1],
            "k--",
            label="Timoshenko",
        )
        ax.plot(
            analytical_unshearable_positon[1],
            analytical_unshearable_positon[0],
            "g-.",
            label="Euler-Bernoulli",
        )

        ax.plot(
            shearable_rod.position_collection[2, :],
            shearable_rod.position_collection[0, :],
            "b-",
            label="n=" + str(shearable_rod.n_elems),
        )
        ax.plot(
            unshearable_rod.position_collection[2, :],
            unshearable_rod.position_collection[0, :],
            "r-",
            label="n=" + str(unshearable_rod.n_elems),
        )

        ax.legend(prop={"size": 12})
        ax.set_ylabel("Y Position (mm)", fontsize=12)
        ax.set_xlabel("X Position (mm)", fontsize=12)
        plt.show()


    plot_timoshenko(shearable_rod, unshearable_rod, end_force)

#if SAVE_RESULTS:
#    import pickle
#
#    filename = "Timoshenko_beam_data.dat"
#    file = open(filename, "wb")
#    pickle.dump(shearable_rod, file)
#    file.close()