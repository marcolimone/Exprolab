# Exprolab Assignment 2 Limone Marco
## Aim of the Assignment
For this assignment we have to add to the previous one the real simulation of a robot running in a indoor enviroment. I have to create a robot model that can detect markers and can move in the enviroment and map it. 

##


## Installation and running procedures
For the dowload and installation of this assignment the user need to go in the *src* folder of his workspace and use the following command:
- git clone https: https://github.com/marcolimone/Exprolab.git

- Then you need to substiute the armor_py_api folder present in the armor folder, with the one present in the repository because some function were added and used in the scripts. 
- Move the updated "marker_publish.cpp" script, in the repository, in the *aruco_ros* folder 
- Update the assignment_2 folder with the one present in the repository
- Add the files "assignment_robot.gazebo" and "assignment_robot.xacro" to the *urdf* folder of the *robot_urdf* folder
- Add the file "motors_config_ass,yaml" to the *config* folder of the *robot_urdf* folder
- Take the "param" folder in the repository and sobstitute the param one in the *planning* folder
- Sobstitute the files "gmapping.launch" and "move_base.launch" with the ones present in the *launch* folder of the *planning* folder


In the end to run the code you need to run two launch file, the first that run the simulation and the second present in the launch folder of the publishers folder, that start all the node and the state machine:
- roslaunch assignment_2 assignment.launch
- roslaunch publishers nodes_launcher.launch 

Note that in the publishers folder there are also some simple subscriber to test individually the nodes.
In the node's script there are some commented line that are used to debug the code.


## Structure of the code
The code is structured as the previous assignment with the difference that now we use gazebo to simulate the robot, a script where the robot model is defined and we use move_base to have the planning of robot movement, and gmapping to map the enviroment. Moreover there is a marker detect node that allow the detection of the markers (this node was already given) and a server (also already given)that given in input the markers ID, give us back the information to create the map.

At this link there is the documentation: https://marcolimone.github.io/Exprolab/


## Working hypothesis and environment
### System’s features
The robot that work in the simulation have an arm with four links and joints:
- a base arm link with a fixed joint that fix the base of the arm to the mobile robot
- a first link that hava a revolute joint that allow a rotation around z-axis used to rotate the camera around 360 degrees
- another link that have a revolute joint that allow a rotation around x-axis used to rotate up and down the camera
- the last link is the camera link that have a fixed joint

The idea is to rotate the camera thanks to the first joint to detect the markers, if some marker is lost we add also a rotation of the second revolute joint to see markers that are in an higher position. When the detection fase is end, the map is created on the ontology than there is the planner fase and the controller one.
Regard the alredy given marker detection node, some modifies were done to allow the publish of the detected ID on the topic *ID_pub*.
From the first assignment some changes have been made to the nodes:
- Create map node: before in this script there were only command that comunicate with the API to create the ontology, now there is a subscriber to the publisher *ID_pub* that receive all the detected markers that are put in an array in the callback, than there is a function that allow the rotation of the joint of the robot during the detection fase, than after the detection of all the markers the function take the array with the IDs and start to call the service to have the information that are used to create te map in the ontology. 
- Controller node: the controller node is very similar to the previous one, with the difference that in the first assignment the movement of the robot was simulated with a time counter, now that we have a real simulation the node subscribe to *odom* to have the actual position of the robot and to estimate the distance between the robot and the goal. When the robot reach the goal all are done all the manipulation of the ontology in the same way as the previous assignment.
- Wait state: the Wait state is managed in the FSM node, in the first assignment in this state was requested to simply wait some time, now in this state the robot need to turn around the camera to inspect it. 
- Battery low node: in the first assignment, all the manipulation of the ontology were done in this node when the battery was low, now when the FSM enter in the Recharge state, it raise up the *controller_flag* and send on the same topic of the planner that it have to reach the E room, in this way all the fase of changing room is managed by the controller and when the robot arrive in the room, a flag *arrived_in_E* set to 1 allow the recharge of the battery. Moreover an "arrived_plan_flag" flag is used to synchronize the battery low node with the controller node, in fact this flag is raised to 1 by the controller when it receives the message sent by the battery low node. The battery low node subsequently checks the flag and when it is equal to 1 it proceeds with its tasks.

### Notes
- note on some problems that sometime occur after the Recharge State: sometimes after the Recharge State when the planner start, the query done to the ontology to have the reacheble room, give back an empty array of reacheble rooms and fails in the choice of the next room to reach. I try to understand what couse the problem, but the only node that interact with the API to modify the ontology is the controller node that in all the other situation work very well. I think could be a problem with the API. 
- note on markers: the marker with ID n17 is rotate respect to the original map due to al lot of fails in its detection. Different robot configuration were tested, but due to the position of the robot respect to the marker all configuration fails. 

### Assumption
Some design choices were made on the basis of some assumptions:
- every time that the camera have to rotate in a room, I decide to make it do two turns, one clockwise and one counterclockwise. In this way the position of the joint can return in the 0.0 position. This is to simplify the managing of the joint, and to avoid some problems that occur when was asked to the joint to change its position of some radians all with one command, infact sometimes it start to oscillate and stack in a position.
- an assumption was made in the markers detection fase, infact knowing that there were 7 markers and the IDs of the markers were between 11 and 17, I decide to discard all detected markers that weren't in this range, and to pass to the next fase where 7 markers where detected. This assumption makes the code less general, but was made to speed up the process for what we need to do.
- the discharge of the battery was slow down due to the fact that now we have a real robot that need some time to reach the designed room.

### System’s limitations
- obviously a limitaton is the problem mentioned in the Note section

### Possible technical Improvements
- a possible future improvement could the implementation of a better way to detect the markers
