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

The state machine is a part of the architecture. It is supported by three nodes that send messages that the state machine will manage:
- Battery low node: this node is contained in the "battery_low_pub.py" file and is used for battery management. The battery is managed by a counter that decreases during the discharge phase and increases during the charge phase, with two different speeds (the discharge speed is faster than the charge one). Furthermore, when the counter (battery) falls below a certain treshold, a message is sent that will allow the state machine to enter the Recharge state to allow charging, when the battery is fully charged a message will be sent that will allow the state machine to exit from the charging status. The treshold is set to 20% of the battery so that the robot has the necessary battery to move into the charging room. The mode of the counter, increasing or decreasing, is managed by giving a flag that is 1 in any state of the state machine, and is set to 0 only during the reload phase.
- Planner node: planner node is managed by the "planner_pub.py" file. Here, through the API interface, the status of the robot and the ontology are queried: which are the reachable areas, of which are urgent. On the basis of the answers obtained, a room to be reached is chosen. After this choice has been made, two messages are published on two different topics, one boolean that will be read by the state machine and will be used to exit the Planner state, the other message contains the room to reach and will be read by the controller node.
- Controller node: controller node simulates the movement of the robot using a sleep. In this node, all the manipulations necessary for moving the robot from one room to another are made. This is done by communicating with Armor via the API interface, in particular the position of the robot in the ontology, and the timestamps of the robot and new room are changed. Finally, a message is published which will be used by the state machine to pass from the Controller state to the Wait state.

