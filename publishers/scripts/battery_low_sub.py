#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool

BATTERY_LOW = 'battery_low'
BATTERY_OK = 'battery_ok'

def callback(msg):
    if msg.data == BATTERY_LOW:
       rospy.loginfo(msg)
       rospy.set_param("/battery_flag", 0)
    elif msg.data == BATTERY_OK:
       rospy.loginfo(msg)
       rospy.set_param("/battery_flag", 1)
def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("battery", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
