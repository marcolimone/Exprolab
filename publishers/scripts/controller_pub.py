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

Publisher to:

 /controller
 
"""



import rospy
import time
import datetime
import calendar
from std_msgs.msg import String
from std_msgs.msg import Bool
from armor_msgs.msg import ArmorDirectiveReq, ArmorDirectiveRes
from armor_api.armor_client import ArmorClient
from os.path import dirname, realpath

count = 0
'''
Count used to simulate the movement of the robot
'''

def callback(msg):

    '''
    This function that is a subscriber callback there is the manipulation of the robot position using the object property "isIn"
    than there is the update of timestamps for Robot1 and the new reached room  using rispectively the object property "now" and "visitedAt"
    in this function are import library "datetime" and "calender" to know the actual date and convert it in UNIX timestamp
    '''
    path = dirname(realpath(__file__))
    path = path +"/../"
    #rospy.loginfo(msg)
    message = msg.data
    global count
    client = ArmorClient("client", "reference")
    pub = rospy.Publisher('controller', Bool, queue_size=10)
    move_to_room = True 
    '''
    message sent where robot reach the room
    ''' 
    
    controller_flag = rospy.get_param("/controller_flag")
    
    if controller_flag == 1:
       time.sleep(0.3)
        
       
       if count >= 3:
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
          
          #client.utils.save_ref_with_inferences(path + "topological_map.owl")
          
       else:   
          count += 0.3
          rospy.loginfo(count)
              	
   	
    	
    	
    	
    
def listener():
    
    '''
    This function is used to initialize the subscriber
    '''
    
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("planner_string", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
