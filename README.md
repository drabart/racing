# Racing AI game

A racing game with semi realistc car handling.
Project also includes a deep learning AI using a NEAT algorithm.
AI learns pretty well and after a couple of generations 
can complete a few laps around the track.

Manual racing
![nt](https://github.com/drabart/racing/assets/48629752/e4093b5e-e4cc-4bbe-9083-5a5314f09100)
AI training
![racing](https://github.com/drabart/racing/assets/48629752/cc22efb7-8e02-42df-979d-4c8a51c6fec6)

## How to run

Just install the necessary libraries:
 - tkinter
 - python-neat

And run the main.py

## Manual controls

You can steer the car using
 - W for accelation
 - A and D for changing steering angle
 - S for breaking
 - R for changing gear to reverse
 - Q for resetting the race

The car maintains the inertia and might need a while to get used to

## Training

You can start AI training by clicking the Train button.
The application will unfortunatelly freeze the GUI (I didn't add multithreading)
but every 5 generations (by default) will render all of the neural models at once

You can controll most of the NEAT algorithm variables using the config-feedforward.txt 
(refer to python-neat docs for informations on how to modify it)
The code running the training is in the main.py file
