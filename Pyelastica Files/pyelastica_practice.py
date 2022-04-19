#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 00:21:16 2022

@author: Neelesh
"""
"""
GETTING STARTED WITH PyElastica:
The aim of this code is to design a system based on the Timoshenko_Beam Case to see if it can 
accurtately represent/estimate the case for estimating loading forces on an FBG sensor.    

"""

import numpy as np
import matplotlib.pyplot as plt

#Import Wrappers,
from elastica.wrappers import BaseSystemCollection, Constraints, Forcing

#Import Cosserat Rod Class
from elastica.rod.cosserat_rod import CosseratRod

#Import Boundary Condition Classes
from elastica.boundary_conditions import OneEndFixedRod
from elastica.external_forces import EndpointForces

#Import Timestepping Functions
from elastica.timestepper.symplectic_steppers import PositionVerlet
from elastica.timestepper import integrate

#from examples.TimoshenkoBeamCase.timoshenko_postprocessing import plot_timoshenko

class TimoshenkoBeamSimulator(BaseSystemCollection, Constraints, Forcing): 
    pass

timoshenko_sim = TimoshenkoBeamSimulator()

    
#Setting up the Test Parameters
n_elem = 25

density = 10000
nu = 0.1
E = 1e6

#For shear modulus of 1e4, nu is 99!

poisson_ratio = 99
shear_modulus = E / (poisson_ratio + 1.0)

start = np.zeros((3,))
direction = np.array([0.0, 0.0, 1.0])
normal = np.array([0.0, 1.0, 0.0])
base_length = 0.085
base_radius = 37e-3
base_area = np.pi * base_radius ** 2


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
    shear_modulus= shear_modulus,
)

timoshenko_sim.append(shearable_rod)

#Adding Boundary Conditions
'''
We need to ensure that one end of the rod is fixed, and we are aiming to constrain
the shearable_rod object using the OneEndFixedRod type of constraint.

We also need to define which node of the rod is being constrained. In our case
because the FBG sensor has 9 gratings in the PAF rail and it is placed in ranges 
from 11-18, we are going to constrain it in its 15th position, and constrain the
direction from positions 11-18.
'''
timoshenko_sim.constrain(shearable_rod).using(
    OneEndFixedRod, constrained_position_idx=(0,), constrained_director_idx=(0,)
)
print("One end of the rod is now fixed in place")



'''
The next boundary condition that needs to be applied is the the endpoint force.
Similar to how the we constrained the system we want the the timoshenko_sim
simulator to add_forcing_to the shearable_rod object using the EndpointForces 
type of forcing. This EndpointForces applies force to both ends of the rod. However,
we want to apply force at only one specific end of the rod, so we do this by specifying
the force vector to be applied at each end: origin_force and end_force.
'''

origin_force = np.array([0.0, 0.0, 0.0])
end_force = np.array([-2.5, 0.0, 0.0])

timoshenko_sim.add_forcing_to(shearable_rod).using(
    EndpointForces, origin_force, end_force
)
print('Forces added to the rod')

#ADD UNSHEARABLE ROD FOR COMPARISON
'''
The unshearavle rod is created to compare with the shearable rod, and provide 
a comparison with an ideal case, to see how well this method can approximate 
using the Cosserat Rod theory.
'''

#Start into the plane
unshearable_start = np.array([0.0, -1.0, 0.0])
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
    #Unshearable rod needs G -> inf, which is achievable with a poisson ratio 
    #of ~ -1.0
    shear_modulus = E / (-0.85 + 1.0),
)

timoshenko_sim.append(unshearable_rod)
timoshenko_sim.constrain(unshearable_rod).using(
    OneEndFixedRod, constrained_position_idx=(0,), constrained_director_idx=(0,)
)

timoshenko_sim.add_forcing_to(unshearable_rod).using(
    EndpointForces, origin_force, end_force
)

print('Unshearable rod set up')

#System Finalization
final_time = 3000 #time in ms
dl = base_length / n_elem
dt = 100 * dl
total_steps = int(final_time / dt)
print('Total steps to take', total_steps)

timestepper = PositionVerlet()


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
        analytical_unshearable_positon[0],
        analytical_unshearable_positon[1],
        "k-.",
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
    ax.set_ylabel("Y Position (m)", fontsize=12)
    ax.set_xlabel("X Position (m)", fontsize=12)
    plt.show()


plot_timoshenko(shearable_rod, unshearable_rod, end_force)