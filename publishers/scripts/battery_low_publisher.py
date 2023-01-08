#!/usr/bin/env python

"""
.. module:: battery_low
   :platform: Unix
   :synopsis: Python module for the controll of battery
.. moduleauthor:: Marco Limone
 
This node simulate charge and discharge of a battery, than publish when the battery is low

Param:
 /battery_flag to know when the battery have to start to charge or discharge
 /arrived_plan_flag 
 /arrived_in_E
 /controller_flag

Publisher to:

 /battery
 
"""


import rospy
import time
import datetime
import calendar
from armor_api.armor_client import ArmorClient
from std_msgs.msg import Bool, String

def talker():
    
    '''
    The talker is the function that change the level of the battery with a different velocity between charge and discharge
    and publish critical status of the battery like when is level is too low or when is full
    -battery_low is the message when the battery is under a battery_threshold and we need to recharge it
    -battery_ok is the message sent when the battery is full
    '''
    
    pub2 = rospy.Publisher('planner_string', String, queue_size=10)
    pub = rospy.Publisher('battery', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    battery_level=100
    '''
    status of the battery
    '''
    battery_low = "battery_low"
    '''
    message sent where the battery is below a threshold
    '''
    battery_ok = "battery_ok"
    '''
    message sent when the battery return full
    '''
    battery_threshold = 20
    '''
    threshold to pass to battery low status
    '''
    pub1 = rospy.Publisher('planner_string', String, queue_size=10)
    battery_flag = rospy.get_param("/battery_flag")
    rospy.loginfo(battery_flag)
    
    count = 0
    '''
    this count is used to allow the movement in the E room only one time
    '''
    
    while not rospy.is_shutdown():
        battery_flag = rospy.get_param("/battery_flag")
        rospy.loginfo(battery_flag)
        if battery_flag == 0:
             if count == 0:
                count = count+1   
                
                rospy.set_param("/controller_flag", 1)
                flag_message = rospy.get_param("/arrived_plan_flag")
                
                while flag_message != 1:
                      pub1.publish("E")
                      flag_message = rospy.get_param("/arrived_plan_flag")
                      time.sleep(1)
             rospy.loginfo(flag_message)   
             arrived = rospy.get_param("/arrived_in_E") 
             
                  
             if arrived == 1:
                   
                if battery_level < 100:
                   battery_level = battery_level +1
                   rospy.loginfo(battery_level)
                   time.sleep(0.2)
                elif battery_level == 100:
                   rospy.set_param("/controller_flag", 0)
                   pub.publish(battery_ok)
                   rospy.loginfo(battery_ok)
                
        elif battery_level > battery_threshold:
             battery_level = battery_level-1
             rospy.loginfo(battery_level)
             time.sleep(8)
        elif battery_level <= battery_threshold:
             count = 0
             pub.publish(battery_low)
             rospy.loginfo(battery_low)
             
             
             

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
