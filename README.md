# Research-Project-Files
Included in this repository is all the raw data, plus the processing methods used to obtain figures/values used in my research project titled: Force Sensing Using Fibre Bragg Grating (FBG) sensors when interacting with soft interfaces for organ manipulation.

The aim of this README is to enable users to navigate through the collection of files required in the research project, and allow the set-up to be adjusted for future research. It should provide you with all the necessary tools to enable data collection with FBG sensors. The code should have informative comments attached to ensure clarity of what the code intends to achieve. Wherever possible photos displaying the raw data, or data post processing has been included to give you an idea of what the project has achieved. The images/graphs produced have provided the basis for many of the figures used in the research project. The project has been broken down into a series of subroutines/tasks to make the whole process easier to follow

Task 1: Displaying the Raw Data Collected
Once the FBG sensor was connected to the computer it was ran through the Labview programme and python to produce the series of JSON files included. The task of displaying the raw curvature data collected was achieved by picking the middle time value, and iterating through each JSON file in increasing force (e.g. starting off with just the dynamometer, 0.5N, 1N...2.5N) and extracting the curvatures value recorded by the FBG sensor and displaying it on a graph for all 5 runs.

Task 2: Changepoint detection using the PELT method as mentioned in Killick et Al. 2012
The next task is to find the harsh breakpoints, which signify a large shift in curvature and apply an algorithm that can accurately detect them, and then apply a line of best fit

Task 3: Using the Cosserat Rod Theory to estimate the change in force the FBG sensor experienced after identifying the force locations
