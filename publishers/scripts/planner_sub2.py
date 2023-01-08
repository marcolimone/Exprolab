#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool



def callback(msg):
    
     rospy.loginfo(msg)
    
    
    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("planner_string", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
