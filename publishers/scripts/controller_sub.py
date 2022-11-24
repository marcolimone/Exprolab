#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool

MOVE = 'moved'

def callback(msg):
    if msg.data == True:
       rospy.loginfo(MOVE)
    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("controller", Bool, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
