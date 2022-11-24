#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool

PLANDONE = 'end_plan'

def callback(msg):
    if msg.data == True:
       rospy.loginfo(PLANDONE)
    
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("planner", Bool, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
