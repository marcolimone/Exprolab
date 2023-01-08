#!/usr/bin/env python

"""
.. module:: controller
   :platform: Unix
   :synopsis: Python module for controll
.. moduleauthor:: Marco Limone
 
This node make the plan to controll the movements of the robot and publish when the robot is arrived

Param:
 /controller_flag to controll the activation of the controller node

Subscribe to:
 /planner_string
 /odom

Publisher to:

 /controller
 /move_base/goal
 
"""



import rospy
import time
import datetime
import calendar
import actionlib
from std_msgs.msg import String
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry
from move_base_msgs.msg import MoveBaseActionGoal
from armor_msgs.msg import ArmorDirectiveReq, ArmorDirectiveRes
from armor_api.armor_client import ArmorClient
from os.path import dirname, realpath

count = 0
actual_x = -6.0
'''
Variable to store actual x coordinate of the robot
'''
actual_y = 11.0
'''
Variable to store actual y coordinate of the robot
'''
x_error=100
y_error=100
room_x=100.0
room_y=100.0

def pose_callback(msg):

    '''
    callback to receive the actual coordinates of robot
    '''
    global actual_x
    global actual_y
    global x_error
    global y_error
    global room_x
    global room_y
    
    
    actual_x=msg.pose.pose.position.x
    actual_y=msg.pose.pose.position.y
    actual_x=float(actual_x)
    actual_y=float(actual_y)
    x_error=abs(room_x-actual_x)
    y_error=abs(room_y-actual_y)
    #rospy.loginfo(x_error)
    #rospy.loginfo(y_error)
    time.sleep(0.1)

def callback(msg):

    '''
    This function that is a subscriber callback, require to the ontology the coordinates to reach, than it set the coordinates as goal to reach for move_base.
    Then after the robot reach the goal, there is the update of the robot position in the ontology using the object property "isIn",
    than there is the update of timestamps for Robot1 and the new reached room  using rispectively the object property "now" and "visitedAt"
    in this function are import library "datetime" and "calender" to know the actual date and convert it in UNIX timestamp
    '''
    path = dirname(realpath(__file__))
    path = path +"/../"
    #rospy.loginfo(msg)
    message = msg.data
    global count
    global actual_x
    global actual_y
    global x_error
    global y_error
    global room_x
    global room_y
    
    client = ArmorClient("client", "reference")
    pub = rospy.Publisher('controller', Bool, queue_size=10)
    pub1= rospy.Publisher('move_base/goal', MoveBaseActionGoal, queue_size=10)
    goal = MoveBaseActionGoal()
    move_to_room = True 
    '''
    message sent where robot reach the room
    ''' 
    rospy.loginfo(message)
    
    
    controller_flag = rospy.get_param("/controller_flag")
    
    if controller_flag == 1:
       time.sleep(0.3)
       if message == "E":
          rospy.set_param("/arrived_plan_flag", 1)
          
       arrived_plan_flag=rospy.get_param("/arrived_plan_flag")   
          
       if count == 0 or arrived_plan_flag==1:
          
          count = count + 1
          room_x = client.query.dataprop_b2_ind("coordinate_x", message)
          room_y = client.query.dataprop_b2_ind("coordinate_y", message)
         
          room_x=str(room_x)
          room_y=str(room_y)
          
          room_x = room_x[3:-13]
          room_y = room_y[3:-13]
          
          
          room_x=int(room_x)
          room_y=int(room_y)
          
          
          room_x=float(room_x)
          room_y=float(room_y)
          
          room_x=room_x/10
          room_y=room_y/10
       
          goal.goal.target_pose.header.frame_id = "map"
          goal.goal.target_pose.pose.position.x = room_x
          goal.goal.target_pose.pose.position.y = room_y
          goal.goal.target_pose.pose.orientation.w = 1.0
          pub1.publish(goal)
       
       battery_flag = rospy.get_param("/battery_flag")
       
        
       
       while x_error > 1.0 or y_error > 1.0:
          
          rospy.loginfo("estimate error")
          
          
          
       
       if x_error < 1.0 and y_error < 1.0:
          
          room_x=100
          room_y=100
          if message == "E":
             rospy.set_param("/arrived_in_E", 1)
             
          
          rospy.loginfo(count)
          actual_room = client.query.objectprop_b2_ind("isIn", "Robot1")
          #rospy.loginfo(actual_room)
          actual_room = actual_room[0][32:-1]
          rospy.loginfo("starting room is:" + actual_room)
          client.manipulation.replace_objectprop_b2_ind("isIn", "Robot1", message, actual_room)
          client.utils.sync_buffered_reasoner()
          #time.sleep(0.3)
          last_time_move = client.query.dataprop_b2_ind("now", "Robot1")
          #rospy.loginfo(last_time_move)
          last_time_move = last_time_move[0][1:-11]
          last_time_visited = client.query.dataprop_b2_ind("visitedAt", message)
          #rospy.loginfo(last_time_visited)
          last_time_visited = last_time_visited[0][1:-11]
          #rospy.loginfo(last_time_visited)
          rospy.loginfo("last movement of robot is at:" + last_time_move)
          rospy.loginfo("last change in that room is at:" + last_time_visited)
          date = datetime.datetime.utcnow()
          utc_time = calendar.timegm(date.utctimetuple())
          new_time_move = str(utc_time)
          rospy.loginfo("new time is:" + new_time_move)
          
          client.manipulation.remove_dataprop_from_ind("now", "Robot1", "Long", last_time_move)
          client.manipulation.remove_dataprop_from_ind("visitedAt", message, "Long", last_time_visited)
          client.manipulation.add_dataprop_to_ind("now", "Robot1", "Long", new_time_move)
          client.manipulation.add_dataprop_to_ind("visitedAt", message, "Long", new_time_move)
          client.utils.sync_buffered_reasoner()
          rospy.loginfo("arrived in room:" + message)
          count = 0
          time.sleep(0.3)
          
          while controller_flag == 1:
              pub.publish(move_to_room)
              controller_flag = rospy.get_param("/controller_flag")
          rospy.set_param("/arrived_plan_flag",0)
          count = 0
          can_reach = client.query.objectprop_b2_ind("canReach", "Robot1")
          rospy.loginfo(can_reach)
          client.utils.sync_buffered_reasoner()
          #client.utils.save_ref_with_inferences(path + "topological_map.owl")
          
       else:   
          controller_flag = rospy.get_param("/controller_flag")
              	
   	
    	
    	
    	
    
def listener():
    
    '''
    This function is used to initialize the subscriber
    '''
    
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("planner_string", String, callback)
    rospy.Subscriber("odom", Odometry, pose_callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    
    listener()
