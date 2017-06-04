#!/usr/bin/python

import rospy
from gazebo_msgs.msg import ModelStates
import sys



class realPositions(object):

    GAZEBO_TOPIC_NAME = "/gazebo/model_states"

    def __init__(self):
        self.locations = {}
        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            msg = rospy.wait_for_message(self.GAZEBO_TOPIC_NAME, ModelStates)
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.GAZEBO_TOPIC_NAME, ModelStates, self.model_states_callback)
        #rate = rospy.Rate(10.0)
        #while not rospy.is_shutdown():
            #rate.sleep()

    def model_states_callback(self, msg):
        for item_name in msg.name:
            item_index=msg.name.index(item_name)
            item_Pose=msg.pose[item_index]
            self.locations[item_name]=item_Pose

    def getPoseOf(self,item):
        try:
            return self.locations[item]
        except:
            return None

    def getPositionOf(self,item):
        try:
            return self.locations[item].position
        except:
            return None

    def getLocations(self):
        try:
            return self.locations
        except:
            return None

