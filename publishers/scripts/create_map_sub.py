#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool

ENDMAP = 'endmap'

def callback(msg):
    if msg.data == True:
       rospy.loginfo(ENDMAP)
    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("send_map", Bool, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
