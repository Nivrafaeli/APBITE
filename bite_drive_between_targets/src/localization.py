#!/usr/bin/python

import rospy
from gazebo_msgs.msg import ModelStates
from apbite_logger.msg import loggerMessage
from geometry_msgs.msg import Transform
import tf

import math
import sys


class localizationPublisher(object):
    GAZEBO_TOPIC_NAME = "/gazebo/model_states"

    def __init__(self, publish_topic_name, robot_name):
        self.robot_name = robot_name
        self.publisher = rospy.Publisher(publish_topic_name, Transform, queue_size=100)
        self.translation_tuple=(0,0,0)
        self.rotatioin_tuple=(0,0,0,0)
        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            msg = rospy.wait_for_message(self.GAZEBO_TOPIC_NAME, ModelStates)
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.GAZEBO_TOPIC_NAME, ModelStates, self.model_states_callback)

    def PoseToTuple(self,pose):
        translation_tuple=(pose.position.x,pose.position.y,pose.position.z)
        rotatioin_tuple=(pose.orientation.x,pose.orientation.y,pose.orientation.z,pose.orientation.w)
        return translation_tuple, rotatioin_tuple

    def model_states_callback(self, msg):
        try:
            robot_index = msg.name.index(self.robot_name)
            robot_pos = msg.pose[robot_index]
            self.translation_tuple, self.rotatioin_tuple = self.PoseToTuple(robot_pos)
        except ValueError:
            rospy.logdebug("Robot %s state is not published by gazebo." % self.robot_name)
            return

if __name__ == "__main__":
    rospy.init_node("localization")

    robot_name = rospy.get_param("~robot_name")
    topic_name = "%s/localization" % robot_name
    publisher=localizationPublisher(topic_name, robot_name)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        br = tf.TransformBroadcaster()
        br.sendTransform(publisher.translation_tuple, publisher.rotatioin_tuple, rospy.Time.now(), robot_name + "/base_link",
                     "/map")
        rate.sleep()
    #rospy.spin()
