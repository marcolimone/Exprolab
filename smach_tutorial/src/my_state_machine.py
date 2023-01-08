#!/usr/bin/env python

"""
.. module:: state machine
   :platform: Unix
   :synopsis: Python module for the state machine
.. moduleauthor:: Marco Limone
 
This node run the state machine the execute function of each state describe what happened in each state 

Param:
 /battery_flag to know when the battery have to start to charge or discharge
 /controller_flag to activate and deactivate the controller
 /planner_flag

Subsciber to:

 /battery
 /create_map
 /planner
 /controller
 
"""



import roslib
import rospy
import smach
import smach_ros
import time
import random
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_msgs.msg import Float64
from threading import Thread, Lock
import threading


BATTERY_LOW = 'battery_low'
END_MAP = 'endmap'
PLAN_OK = 'plan_ok'
ARRIVED = 'arrived'
END_TIME = 'endtime'
BATTERY_OK = 'battery_ok'


class Helper:
    '''
    Class that allow the use of mutex and contain all the callback of the subscribers 

    '''
    def __init__(self, done_callback = None, feedback_callback = None, mutex = None):
        rospy.Subscriber("battery", String, self.batterylowCallback)
        rospy.Subscriber("send_map", Bool, self.buildingmapCallback)
        rospy.Subscriber("planner", Bool, self.plannerCallback)
        rospy.Subscriber("controller", Bool, self.controllerCallback)
        if mutex is None:
            self.mutex = Lock()
        else:
            self.mutex = mutex
            
        self.change_state = BATTERY_OK    

    def batterylowCallback(self, msg):
        '''
        Args:String return the status of the battery
        '''
        self.mutex.acquire()
        if msg.data == BATTERY_LOW:
           self.change_state = BATTERY_LOW
           rospy.loginfo(BATTERY_LOW)
        elif msg.data == BATTERY_OK:  
           self.change_state = BATTERY_OK
           rospy.loginfo(BATTERY_OK)
        self.mutex.release()
        
           
    def buildingmapCallback(self, msg):
        '''
        Args:Bool this value is true when the building of the map is end
        '''
        if msg.data == True:
           self.mutex.acquire()
           self.change_state = END_MAP
           self.mutex.release()
           rospy.loginfo(END_MAP) 
           
    def plannerCallback(self, msg):
        '''
        Args:Bool this value is true when the planner send a plan
        '''
        if msg.data == True:
           self.mutex.acquire()
           self.change_state = PLAN_OK
           self.mutex.release()
           rospy.loginfo(PLAN_OK)        
     
    def controllerCallback(self, msg):
        '''
        Args:Bool this value is true when the controller node brings the robot in the right room
        '''
        if msg.data == True:
           self.mutex.acquire()
           self.change_state = ARRIVED
           self.mutex.release()
           rospy.loginfo(ARRIVED)                   



# define state Building_map
class Building_map(smach.State):

    '''
    This class describe what happen when the state machine is in the Building_map state, the state machine exit from this state when the ontology is finish.
    
    '''

    def __init__(self):
        
        self._helper = Helper()
        smach.State.__init__(self, 
                             outcomes=['endmap','battery_low', 'plan_ok', 'arrived', 'endtime', 'battery_ok'],
                             input_keys=['unlocked_counter_in'],
                             output_keys=['unlocked_counter_out'])
        
    def execute(self, userdata):
        
        while not rospy.is_shutdown():
                  
                  try:
                      self._helper.mutex.acquire()
                      if self._helper.change_state == BATTERY_LOW:
                         return self._helper.change_state
                      elif self._helper.change_state == END_MAP: 
                         return self._helper.change_state
                         
                      rospy.loginfo('Executing state Building_map')
                  finally:    
                      self._helper.mutex.release()
                  rospy.sleep(0.3)    
    

# define state Planner
class Planner(smach.State):

    '''
    This class describe what happen when the state machine is in the Planner state, to exit from this state the robot need to choose the room where the robot have to go.
    Another way to exit from this state is when arrive the message of battery low.
    
    '''
    
    def __init__(self):
        self._helper = Helper()
        smach.State.__init__(self, 
                             outcomes=['endmap','battery_low', 'plan_ok', 'arrived', 'endtime', 'battery_ok'],
                             input_keys=['locked_counter_in'],
                             output_keys=['locked_counter_out'])

    def execute(self, userdata):
        rospy.set_param("/battery_flag", 1)
        rospy.set_param("/controller_flag", 0)
        rospy.set_param("/planner_flag", 1)
        rospy.set_param("/arrived_in_E", 0)
        while not rospy.is_shutdown():
                  try:
                      self._helper.mutex.acquire()
                      if self._helper.change_state == BATTERY_LOW:
                         return self._helper.change_state
                      elif self._helper.change_state == PLAN_OK:
                         return self._helper.change_state
                      rospy.loginfo('Executing state Planner')
                  finally:    
                      self._helper.mutex.release()
                  rospy.sleep(0.3) 
                  rospy.loginfo('Executing state Planner')
              
    
# define state Controller
class Controller(smach.State):

    '''
    This class describe what happen when the state machine is in the Controller state, to exit from this state the robot need to reach the desired room.
    Another way to exit from this state is when arrive the message of battery low.
    
    '''
    
    def __init__(self):
        
        self._helper = Helper()
        smach.State.__init__(self, 
                             outcomes=['endmap','battery_low', 'plan_ok', 'arrived', 'endtime', 'battery_ok'],
                             input_keys=['unlocked_counter_in'],
                             output_keys=['unlocked_counter_out'])
        
    def execute(self, userdata):
        rospy.set_param("/planner_flag", 0)
        rospy.set_param("/controller_flag", 1)
        while not rospy.is_shutdown():
                  
                  try:
                      self._helper.mutex.acquire()
                      if self._helper.change_state == BATTERY_LOW:
                         return BATTERY_LOW
                      if self._helper.change_state == ARRIVED:
                         return ARRIVED
                      rospy.loginfo('Executing state Controller')
                  finally:   
                      self._helper.mutex.release()
                  rospy.sleep(0.3) 
        
        

# define state Wait
class Wait(smach.State):

    '''
    This class describe what happen when the state machine is in the Wait state, to exit from this state the robot need turn its camera around, at the end of this motion the state machine can change state.
    Another way to exit from this state is when arrive the message of battery low.
    '''
    
    def __init__(self):
        self._helper = Helper()
        smach.State.__init__(self, 
                             outcomes=['endmap','battery_low', 'plan_ok', 'arrived', 'endtime', 'battery_ok'],
                             input_keys=['locked_counter_in'],
                             output_keys=['locked_counter_out'])

    def execute(self, userdata):
        rospy.set_param("/planner_flag", 0)
        pub = rospy.Publisher('rob/joint1_position_controller/command', Float64, queue_size=10)
        rospy.set_param("/controller_flag", 0)
        rotation=0.0
        rotation_flag=0
        finish=0
        pub.publish(rotation)
        while not rospy.is_shutdown():
                  rospy.loginfo(finish)
                  try:
                      self._helper.mutex.acquire()
                      if self._helper.change_state == BATTERY_LOW:
                         rotation=0.0
                         pub.publish(rotation)
                         return BATTERY_LOW
                         rospy.loginfo('Executing state Wait')
                      elif  finish == 1 :
                         self._helper.change_state = END_TIME
                         return END_TIME
                         rospy.loginfo('Executing state Wait')   
                  finally :   
                      self._helper.mutex.release()
                  rospy.sleep(0.3)
                  rospy.loginfo('Executing state Wait')
                  if rotation >=6.28:
                     rotation_flag = 1
                  elif rotation < 0.0:
                     finish = 1
                     #rospy.loginfo(finish)
                     rotation_flag = 0
                  
                  if rotation_flag == 1: 
                     rotation = rotation - 0.1
                     pub.publish(rotation)
                  elif rotation_flag == 0:
                     rotation = rotation + 0.1
                     pub.publish(rotation) 
       
        
        
                      

# define state Recharge
class Recharge(smach.State):
    
    '''
    This class describe what happen when the state machine is in the Recharge state, to exit from this state the robot need to go in a defined room to recharge
    when the battery is full, the state can change
    '''
    
    def __init__(self):
        self._helper = Helper()
        smach.State.__init__(self, 
                             outcomes=['endmap','battery_low', 'plan_ok', 'arrived', 'endtime', 'battery_ok'],
                             input_keys=['locked_counter_in'],
                             output_keys=['locked_counter_out'])

    def execute(self, userdata):
        rospy.set_param("/planner_flag", 0)
        rospy.set_param("/battery_flag", 0)
        while not rospy.is_shutdown():
                  
                  try:
                      self._helper.mutex.acquire()
                      if self._helper.change_state == BATTERY_OK:
                         return self._helper.change_state
                         rospy.set_param("/battery_flag", 1)
                         rospy.loginfo('Executing state Recharge')
                  finally :   
                      self._helper.mutex.release()
                  rospy.sleep(0.3)
        
        
            
        
def main():

    '''
    This function initialize and run the state machine with its state and its transitions
    '''
   
    rospy.init_node('smach_state_machine')
    

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['container_interface'])
    sm.userdata.sm_counter = 0

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('BUILDINGMAP', Building_map(), 
                               transitions={'endmap':'PLANNER', 
                                            'battery_low':'RECHARGE',
                                            'plan_ok':'BUILDINGMAP',
                                            'arrived':'BUILDINGMAP',
                                            'endtime':'BUILDINGMAP',
                                            'battery_ok':'BUILDINGMAP'},
                               remapping={'locked_counter_in':'sm_counter', 
                                          'locked_counter_out':'sm_counter'})
        smach.StateMachine.add('PLANNER', Planner(), 
                               transitions={'endmap':'PLANNER',
                                            'battery_low':'RECHARGE',
                                            'plan_ok':'CONTROLLER',
                                            'arrived':'PLANNER',
                                            'endtime':'PLANNER',
                                            'battery_ok':'PLANNER'},
                               remapping={'unlocked_counter_in':'sm_counter',
                                          'unlocked_counter_out':'sm_counter'})
         
                                                                   
        smach.StateMachine.add('CONTROLLER', Controller(), 
                               transitions={'endmap':'CONTROLLER', 
                                            'battery_low':'RECHARGE',
                                            'plan_ok':'CONTROLLER',
                                            'arrived':'WAIT',
                                            'endtime':'CONTROLLER',
                                            'battery_ok':'CONTROLLER'},
                               remapping={'locked_counter_in':'sm_counter', 
                                          'locked_counter_out':'sm_counter'})
                                                                         
        smach.StateMachine.add('WAIT', Wait(), 
                               transitions={'endmap':'WAIT',
                                            'battery_low':'RECHARGE',
                                            'plan_ok':'WAIT',
                                            'arrived':'WAIT',
                                            'endtime':'PLANNER',
                                            'battery_ok':'WAIT'},
                               remapping={'locked_counter_in':'sm_counter', 
                                          'locked_counter_out':'sm_counter'})                                  
        smach.StateMachine.add('RECHARGE', Recharge(), 
                               transitions={'endmap':'RECHARGE',
                                            'battery_low':'RECHARGE',
                                            'plan_ok':'RECHARGE',
                                            'arrived':'RECHARGE',
                                            'endtime':'RECHARGE',
                                            'battery_ok':'PLANNER'},
                               remapping={'locked_counter_in':'sm_counter', 
                                          'locked_counter_out':'sm_counter'})                                  
                                          


    # Create and start the introspection server for visualization
    sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()
    
    
    

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    
    main()
    
    
