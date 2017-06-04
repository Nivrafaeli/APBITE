#!/usr/bin/env python

from beginner_tutorials.srv import *
import rospy

def handle_add_two_ints(req):
    print "Returning [%s + %s = %s]"%(req.a, req.b, (req.a + req.b))
    return AddTwoIntsResponse(req.a + req.b)

def add_two_ints_server():
    rospy.init_node('getRealLocations_server')
    s = rospy.Service('getRealLocations', AddTwoInts, handle_add_two_ints)
    print "Ready to add two ints."
    rospy.spin()

if __name__ == "__main__":
    add_two_ints_server()



import rospy
from gazebo_msgs.msg import ModelStates
from apbite_logger.msg import loggerMessage
import math
import sys

LOCATIONS={}

class trueMeasurmentPublisher(object):
    GAZEBO_TOPIC_NAME = "/gazebo/model_states"

    def __init__(self, publish_topic_name, robot_name, target_list, obstacle_list):
        self.robot_name = robot_name

        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            msg = rospy.wait_for_message(self.GAZEBO_TOPIC_NAME, ModelStates)
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.GAZEBO_TOPIC_NAME, ModelStates, self.model_states_callback)

    def model_states_callback(self, msg):
        try:
            robot_index = msg.name.index(self.robot_name)
        except ValueError:
            rospy.logdebug("Robot %s state is not published by gazebo." % self.robot_name)
            return
        robot_pos = msg.pose[robot_index].position
        LOCATIONS[self.robot_name]=robot_pos
        # going over the targets
        for target_name in self.target_list:
            # if we already reached this target once no need to report about again
            try:
                my_index = msg.name.index(target_name)
            except ValueError:
                rospy.logdebug("target %s state is not published by gazebo." % target_name)
                continue
            target_pose = msg.pose[my_index].position
            LOCATIONS[target_name] = target_pose
        # going over the obsticals
        for obstical_name in self.obstacle_list:
            try:
                my_index = msg.name.index(obstical_name)
            except ValueError:
                rospy.logdebug("target %s state is not published by gazebo." % obstical_name)
                continue
            obs_pose = msg.pose[my_index].position
            LOCATIONS[obstical_name] = obs_pose

def getLocations():
    return LOCATIONS

if __name__=="__main__":
    rospy.init_node("true_measurment")

    robot_name = rospy.get_param("~robot_name")
    min_distance_target = rospy.get_param("~min_distance_target")
    min_distance_obstacle = rospy.get_param("~min_distance_obstacle")
    target_list = rospy.get_param("~targets").split(',')
    target_list = [target.strip() for target in target_list]
    obstical_list = rospy.get_param("~obstacles").split(',')
    obstical_list = [obstical.strip() for obstical in obstical_list]
    topic_name = "results_%s" % robot_name
    trueMeasurmentPublisher(topic_name, robot_name, min_distance_target, min_distance_obstacle, target_list, obstical_list)
    rospy.spin()