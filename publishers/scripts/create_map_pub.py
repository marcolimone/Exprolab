#!/usr/bin/env python

"""
.. module:: create_map
   :platform: Unix
   :synopsis: Python module for the creation of the map
.. moduleauthor:: Marco Limone
 
This node create the ontology of a map they receive information from markers located in the map. To detect the markers messages are published to rotate the camera. It publish a message when it has done


Publisher to:

 /send_map
 /rob/joint1_position_controller/command
 /rob/joint4_position_controller/command

Service:
 /room_info 
"""




import rospy
import time
import datetime
import calendar
import threading
import actionlib
from std_msgs.msg import Bool
from std_msgs.msg import Int32
from std_msgs.msg import Float64
from armor_msgs.msg import ArmorDirectiveReq, ArmorDirectiveRes
from armor_api.armor_client import ArmorClient
from os.path import dirname, realpath
from assignment2.srv import *

endmap = True
'''
message sent after the building of the map
'''
id_array=list()
'''
list whith all the detected ID
'''
doors=list()
'''
list of doors for each room
'''
rotation = 0.0
'''
variable used as message to control the joint that allow the camera rotation
'''
n_marker = 0
'''
variable to know the number of detected markers
'''

def rotation_camera():
    
    '''
    This function allow the rotation of the camera, than create the map requesting information from the appropriate service
    '''
    pub1 = rospy.Publisher('send_map', Bool, queue_size=10)
    pub = rospy.Publisher('rob/joint1_position_controller/command', Float64, queue_size=10)
    pub2 = rospy.Publisher('rob/joint4_position_controller/command', Float64, queue_size=10)
    client = ArmorClient("client", "reference")
    global id_array
    global rotation
    global n_marker
    
    path = dirname(realpath(__file__))
    path = path +"/../"
    
    rotation_flag=0
    up_down=0.0
    
    while n_marker < 7:
    
       if rotation >=6.28:
          rotation_flag = 1
          up_down=0.1
          pub2.publish(up_down)
       elif rotation <= 0.0:
          rotation_flag = 0  
          up_down=0.0 
          pub2.publish(up_down)
      
       if rotation_flag == 1:  
          rotation = rotation - 0.01
          pub.publish(rotation)
          
       elif rotation_flag == 0:
          rotation = rotation + 0.01
          pub.publish(rotation)  
       time.sleep(0.3)
    
    
    while rotation > 0.1:
          rotation = rotation - 0.01
          pub.publish(rotation)
          time.sleep(0.1)  
    pub2.publish(0.0)
    
    if n_marker >= 7:
       date = datetime.datetime.utcnow()
       utc_time = calendar.timegm(date.utctimetuple())
       new_time = str(utc_time)
       rospy.loginfo("new time is:" + new_time)
       info = rospy.ServiceProxy('room_info', RoomInformation)
       for i in range(0,n_marker):
          resp = info(id_array[i])
          
          resp_room=resp.room
          client.manipulation.add_dataprop_to_ind("visitedAt", resp_room, "Long", new_time)
          x=resp.x
          y=resp.y
          x=x*10
          y=y*10
          x=int(x)
          y=int(y)
          
          x=str(x)
          y=str(y)
          
          
          client.manipulation.add_dataprop_to_ind("coordinate_x", resp_room, "Long", x)
          client.manipulation.add_dataprop_to_ind("coordinate_y", resp_room, "Long", y)
          
          resp_connections=resp.connections
          rospy.loginfo(resp_room)
          rospy.loginfo(resp_connections)
          conn_lenght=len(resp_connections)
          rospy.loginfo(conn_lenght)
          
          for m in range(0,conn_lenght):
              
              doors.append(resp_connections[m].through_door)
              client.manipulation.add_objectprop_to_ind("hasDoor", resp_room, resp_connections[m].through_door)
              
          
          rospy.loginfo(doors) 
          del doors[0:conn_lenght]
           
       
       
          
       client.manipulation.disj_inds_of_class('LOCATION')
       client.manipulation.disj_inds_of_class('ROOM')
       client.manipulation.disj_inds_of_class('DOOR')
       client.manipulation.disj_inds_of_class('CORRIDOR')
       client.manipulation.disj_inds_of_class('URGENT') 
       
       client.manipulation.add_objectprop_to_ind("isIn", "Robot1", "E")
       
       client.utils.apply_buffered_changes()
       client.utils.sync_buffered_reasoner()
       '''
       client.utils.save_ref_with_inferences(path + "topological_map.owl")
       '''
       i=0
       while i <= 5:
          pub1.publish(endmap)
          rospy.loginfo('sended map')
          time.sleep(1)
          i = i+1


def ID_callback(msg):

    '''
    This function take in to account the detected markers and how much they are
    
    '''
    
    
    global n_marker
    global id_array
    
    
    n_id=msg.data
    
    if n_id<18 and n_id>10:
       response = n_id in id_array
        
       if response == False:
          id_array.append(n_id)
       '''
       rospy.loginfo(id_array)
       '''
    
    n_marker=len(id_array)
    
          
    
def listener():
    
    
    
    path = dirname(realpath(__file__))
    path = path +"/../"
    

    client = ArmorClient("client", "reference")
    client.utils.load_ref_from_file(path + "topological_map.owl", "http://bnc/exp-rob-lab/2022-23",
                                True, "PELLET", True, False)  # initializing with buffered manipulation and reasoning
    client.utils.mount_on_ref()
    client.utils.set_log_to_terminal(True)
    
    rospy.init_node('listener', anonymous=True)
    
    t1 = threading.Thread(target=rotation_camera, name="rotation")
    t1.start()
    
    rospy.Subscriber("ID_pub", Int32, ID_callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    
    
    listener()
    
