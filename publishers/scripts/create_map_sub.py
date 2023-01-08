#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Int32

ENDMAP = 'endmap'
id_array=list()
def callback(msg):
    
    rospy.loginfo(msg)
    
    
   
    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("send_map", Bool, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
