#!/usr/bin/env python

"""
.. module:: planner
   :platform: Unix
   :synopsis: Python module for planning
.. moduleauthor:: Marco Limone
 
This node make the plan to know where te robot have to go

Param:
 /planner_flag controll the activation of the planner

Publisher to:

 /planner
 /planner_string
 
"""


import rospy
import time
import random
from std_msgs.msg import Bool, String
from armor_msgs.msg import ArmorDirectiveReq, ArmorDirectiveRes
from armor_api.armor_client import ArmorClient
from os.path import dirname, realpath
import numpy as np
 



urgent_array = [False, False, False, False]

def talker():
    
    '''
    In this function are done some query to understund which is the room where te robot has to go:
    -query to know witch room Robot1 "canReach"
    -query to know the CLASSes of the reachble rooms to know if there are URGENT rooms, is done in a for loop that depend on the lenght of the response array of reachble rooms
    for every query there are some string manipulations to adapt messages to the args of the querys
    
    there are to publishers:
    /planner that publish a boolean that will be read from the state machine
    /planner_string that publish a string with the room to reach that wiil be read from the controll node
    
    before publish the two value a check is done to know how much URGENT room there are. if there is only a URGENT room is send this one, if the URGENT roooms are 0 or more than 1 there is a random choice.
    '''
    plan_done = True
    '''
    message sent at the and of the planning
    '''
    
    pub1 = rospy.Publisher('planner', Bool, queue_size=10)
    pub2 = rospy.Publisher('planner_string', String, queue_size=10)
    rospy.init_node('client', anonymous=True)
    
    path = dirname(realpath(__file__))
    path = path +"/../"
    
   
    
    client = ArmorClient("client", "reference")
    
    '''
    client.utils.sync_buffered_reasoner()
    '''
    while not rospy.is_shutdown():
       planner_flag = rospy.get_param("/planner_flag")
       while planner_flag == 1:
        
           client.manipulation.disj_inds_of_class('LOCATION')
           client.manipulation.disj_inds_of_class('ROOM')
           client.manipulation.disj_inds_of_class('DOOR')
           client.manipulation.disj_inds_of_class('CORRIDOR')
           client.manipulation.disj_inds_of_class('URGENT')
           client.utils.sync_buffered_reasoner()
        
           urgent_array = [False, False, False, False]
           client.utils.sync_buffered_reasoner()
           can_reach = client.query.objectprop_b2_ind("canReach", "Robot1")
           number=len(can_reach)
           urgent_count = 0
           rospy.loginfo(can_reach)
           rospy.loginfo(number)
           for i in range(0,number):
               can_reach[i] = can_reach[i][32:-1]
           rospy.loginfo(can_reach)      
           for n in range (0,number):
               classes = client.query.class_b2_ind(can_reach[n], "false")  
               classes_len = len(classes)
               rospy.loginfo(classes_len)
            
               rospy.loginfo(can_reach[n])
               rospy.loginfo(classes)
               for k in range (0,classes_len):
                   response = "URGENT" in classes[k]
                   rospy.loginfo(response) 
                   if response == True:
                      urgent_array[n] = True
                      urgent_count = urgent_count +1
        
           rospy.loginfo(urgent_array)
           rospy.loginfo(urgent_count)
           #urgent_rooms = np.empty(shape=urgent_count)
           urgent_rooms = list()
        
           for m in range (0,len(urgent_array)):
               if urgent_array[m] == True:
                  #urgent_rooms[m] = can_reach[m]
                  urgent_rooms.append(can_reach[m])
        
        
           rospy.loginfo(urgent_rooms)  
        
           if urgent_count > 0:
        
              chosed_room=random.choice(urgent_rooms)  
              rospy.loginfo("choosed room is" + chosed_room) 
              message = chosed_room
           
           else:
              chosed_room=random.choice(can_reach)  
              rospy.loginfo("choosed room is " + chosed_room) 
              message = chosed_room 
        
           room = client.query.objectprop_b2_ind("isIn", "Robot1") 
           room = room[0][32:-1]
        
           flag = rospy.get_param("/battery_flag")
           flag_message = rospy.get_param("/planner_flag")
           rospy.loginfo(flag)
           while flag_message != 0 and flag == 1:
              flag = rospy.get_param("/battery_flag")
              flag_message = rospy.get_param("/planner_flag")     
              #rospy.loginfo(message)
              pub1.publish(plan_done)
              #rospy.loginfo("send ok")
              pub2.publish(message)
              #rospy.loginfo("send plan")
              time.sleep(1)
        
        
           
              
           
           planner_flag = rospy.get_param("/planner_flag")
           client.utils.apply_buffered_changes()
           client.utils.sync_buffered_reasoner()
        #client.utils.save_ref_with_inferences(path + "topological_map.owl")
    	   
    
if __name__ == '__main__':
    
    try:
        time.sleep(4)
        talker()
    except rospy.ROSInterruptException:
        pass
