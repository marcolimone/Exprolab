#!/usr/bin/env python

"""
.. module:: create_map
   :platform: Unix
   :synopsis: Python module for the creation of the map
.. moduleauthor:: Marco Limone
 
This node create the ontology of a map then publish when it has done


Publisher to:

 /send_map
 
"""




import rospy
import time
import datetime
import calendar
from std_msgs.msg import Bool
from armor_msgs.msg import ArmorDirectiveReq, ArmorDirectiveRes
from armor_api.armor_client import ArmorClient
from os.path import dirname, realpath

endmap = True
'''
message sent after the building of the map
'''

def talker():

    '''
    This function create the ontology using API commands, then publish a message when it has finish 
    -client is a variable of type ArmorClient that include all the method to make correctly the call to Armor server
    
    '''
    pub = rospy.Publisher('send_map', Bool, queue_size=10)
    rospy.init_node('client', anonymous=True)
    path = dirname(realpath(__file__))
    path = path +"/../"
    

    client = ArmorClient("client", "reference")
    client.utils.load_ref_from_file(path + "topological_map.owl", "http://bnc/exp-rob-lab/2022-23",
                                True, "PELLET", True, False)  # initializing with buffered manipulation and reasoning
    client.utils.mount_on_ref()
    client.utils.set_log_to_terminal(True)
    
    
          
    client.manipulation.add_objectprop_to_ind("hasDoor", "E", "D5")
    rospy.loginfo('E ha D5') 
    
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "E", "D6")
    rospy.loginfo('E ha D6') 
    
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C1", "D1")
    rospy.loginfo('C1 ha D1')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C1", "D2")
    rospy.loginfo('C1 ha D2')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C1", "D5")
    rospy.loginfo('C1 ha D5')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C1", "D7")
    rospy.loginfo('C1 ha D7')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C2", "D3")
    rospy.loginfo('C2 ha D3')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C2", "D4")
    rospy.loginfo('C2 ha D4')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C2", "D6")
    rospy.loginfo('C2 ha D6')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "C2", "D7")
    rospy.loginfo('C2 ha D7')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "R1", "D1")
    rospy.loginfo('R1 ha D1')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "R2", "D2")
    rospy.loginfo('R2 ha D2')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "R3", "D3")
    rospy.loginfo('R3 ha D3')
    
    client.manipulation.add_objectprop_to_ind("hasDoor", "R4", "D4")
    rospy.loginfo('R4 ha D4')
   
    client.manipulation.disj_inds_of_class('LOCATION')
    client.manipulation.disj_inds_of_class('ROOM')
    client.manipulation.disj_inds_of_class('DOOR')
    client.manipulation.disj_inds_of_class('CORRIDOR')
    client.manipulation.disj_inds_of_class('URGENT')
    
    rospy.loginfo('disjoint')
    
    
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    new_time = str(utc_time)
    rospy.loginfo("new time is:" + new_time)
    
    client.manipulation.add_dataprop_to_ind("visitedAt", "E", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "C1", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "C2", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "R1", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "R2", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "R3", "Long", new_time)
    client.manipulation.add_dataprop_to_ind("visitedAt", "R4", "Long", new_time)
    
    client.manipulation.add_objectprop_to_ind("isIn", "Robot1", "E")
    rospy.loginfo('Robot in E')
    
    
    client.utils.apply_buffered_changes()
    client.utils.sync_buffered_reasoner()
    i = 0
    #client.utils.save_ref_with_inferences(path + "topological_map.owl")
    while i <= 5:
          pub.publish(endmap)
          rospy.loginfo('sended map')
          time.sleep(1)
          i = i+1
          
    while not rospy.is_shutdown():      
          rospy.loginfo('end process')
          time.sleep(30)

if __name__ == '__main__':
    
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
    
