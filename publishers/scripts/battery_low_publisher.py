#!/usr/bin/env python

"""
.. module:: battery_low
   :platform: Unix
   :synopsis: Python module for the controll of battery
.. moduleauthor:: Marco Limone
 
This node simulate charge and discharge of a battery, than publish when the battery is low

Param:
 /battery_flag to know when the battery have to start to charge or discharge

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
    battery_flag = rospy.get_param("/battery_flag")
    rospy.loginfo(battery_flag)
    client = ArmorClient("client", "reference")
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
                actual_room = client.query.objectprop_b2_ind("isIn", "Robot1")
                actual_room = actual_room[0][32:-1]
                #rospy.loginfo("starting room is:" + actual_room)
                client.manipulation.replace_objectprop_b2_ind("isIn", "Robot1", "E", actual_room)
                client.utils.sync_buffered_reasoner()
                last_time_move = client.query.dataprop_b2_ind("now", "Robot1")
                last_time_move = last_time_move[0][1:-11]
                last_time_visited = client.query.dataprop_b2_ind("visitedAt", "E")
                last_time_visited = last_time_visited[0][1:-11]
                date = datetime.datetime.utcnow()
                utc_time = calendar.timegm(date.utctimetuple())
                new_time_move = str(utc_time)
                client.manipulation.remove_dataprop_from_ind("now", "Robot1", "Long", last_time_move)
                client.manipulation.remove_dataprop_from_ind("visitedAt", "E", "Long", last_time_visited)
                client.manipulation.add_dataprop_to_ind("now", "Robot1", "Long", new_time_move)
                client.manipulation.add_dataprop_to_ind("visitedAt", "E", "Long", new_time_move)
                client.utils.sync_buffered_reasoner()
             if battery_level < 100:
                battery_level = battery_level +1
                rospy.loginfo(battery_level)
                time.sleep(0.2)
             elif battery_level == 100:
                pub.publish(battery_ok)
                rospy.loginfo(battery_ok)
                
        elif battery_level > battery_threshold:
             battery_level = battery_level-1
             rospy.loginfo(battery_level)
             time.sleep(3)
        elif battery_level <= battery_threshold:
             count = 0
             pub.publish(battery_low)
             rospy.loginfo(battery_low)
             
             
             

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
