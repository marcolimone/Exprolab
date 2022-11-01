# Exprolab Assignment 1 Limone Marco
## Aim of the Assignment
For this assignment we have to simulate the presence of a robot in an indoor environment created through ontology. Through the use of a state machine and external nodes, the robot must be able to move around the various rooms, preferring the most urgent ones and always trying to stay in the corridors after being in a room.

##


## Installation and running procedures
For the dowload and installation of this assignment the ser need to go in the *src* folder of his workspace and use the following command:
- git clone https://github.com/marcolimone/Exprolab.git

Then to run the code need to run a launch file that start all the node and the state machine:
- 


## Commented code


## Working hypothesis and environment
### System’s features and assumption
The state machine has been designed on 5 states:
- Send Map: state that runs only once at the beginning. In this state the state machine waits for the map to be created in the ontology, as soon as the ontology is       completed, the state machine will receive the message "end_map" will allow the transition to the next state.
- Planner: in this state the state machine waits until the planner decides which room to reach next. Once the room has been chosen, the state machine will receive the "chosen_room" message which will allow the transition to the next state.
- Controller: the controller state has been designed to simulate the movement of the robot from one room to another (the actual movement is actually instantaneous). When the state machine gets the "arrived" message, it will change the state.
- Wait: in the wait state it simply waits for the time when the robot stops in the room just reached to end.
-Recharge: the state machine moves into this state to allow the robot to recharge before it discharges. This state can be reached from any other state (except the send_map state) when the "battery_low" message arrives. This state is exited when the "battery_ok" message arrives.
