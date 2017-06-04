#!/usr/bin/python

import rospy
from gazebo_msgs.msg import ModelStates
from apbite_logger.msg import loggerMessage
import math
import sys
from RealPositions import *

class trueMeasurmentPublisher(object):
    GAZEBO_TOPIC_NAME = "/gazebo/model_states"

    def __init__(self, publish_topic_name, robot_name, min_distance_target, min_distance_obstacle, target_list, obstacle_list):
        self.robot_name = robot_name
        self.target_list = {target_name:False for target_name in target_list}
        self.obstacle_list = {obstacle_name:True for obstacle_name in obstacle_list}
        self.printed_obstacle_list = {obstacle_name: True for obstacle_name in obstacle_list}
        self.publisher = rospy.Publisher(publish_topic_name, loggerMessage, queue_size=100)
        self.min_distance_target = min_distance_target
        self.min_distance_obstacle = min_distance_obstacle
        self.realPositions = realPositions()
        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            msg = rospy.wait_for_message(self.GAZEBO_TOPIC_NAME, ModelStates)
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.GAZEBO_TOPIC_NAME, ModelStates, self.model_states_callback)

        #Print marker location data




    def calcDist(self,a,b):
        return math.sqrt((a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2)

    def PositionToString(self,position):
        return ","+str(position.x)+","+str(position.y)+","+str(position.z)

    def model_states_callback(self, msg):
        time_Stemp = rospy.Time.now()
        robot_pos = self.realPositions.getPositionOf(self.robot_name)
        # going over the targets
        for target_name in self.target_list:
            # if we already reached this target once no need to report about again
            if self.target_list[target_name]:
                continue
            try:
                target_pose = self.realPositions.getPositionOf(str(target_name))
                distance=self.calcDist(target_pose,robot_pos)
                if distance <= self.min_distance_target:
                    self.target_list[target_name] = True
                    logger_msg = loggerMessage()
                    logger_msg.time_stamp = time_Stemp
                    logger_msg.object_name = "Target {0} ,{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}".format(target_name,
                                                                                                             "", "", "", "",
                                                                                                             distance,"","","",
                                                                                                             target_pose.x,
                                                                                                             target_pose.y,
                                                                                                             target_pose.z,
                                                                                                             robot_pos.x,
                                                                                                             robot_pos.y,
                                                                                                             robot_pos.z)

                    #logger_msg.distance = distance
                    logger_msg.distance = 0
                    self.publisher.publish(logger_msg)
            except:
                pass

        #Prin all obstacles one time
        '''
        for obstical_name in self.obstacle_list:
            if self.printed_obstacle_list[obstical_name]:
                try:
                    self.printed_obstacle_list[obstical_name] = False
                    obs_pose = self.realPositions.getPositionOf(obstical_name)
                    logger_msg = loggerMessage()
                    logger_msg.time_stamp = rospy.Time.now()
                    obstical_name = obstical_name.replace("free_marker_", "")
                    logger_msg.object_name = "Obst pos {0} ,{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}".format(
                        obstical_name, "", "", "", "", "", "", "", "", obs_pose.x, obs_pose.y, obs_pose.z, "", "",
                        "")
                    logger_msg.distance = 2.0
                    self.publisher.publish(logger_msg)

                except:
                    pass
            '''
        # going over the obsticals
        for obstical_name in self.obstacle_list:

            try:
                obs_pose=self.realPositions.getPositionOf(obstical_name)
                distance = self.calcDist(obs_pose, robot_pos)

                # if the are near an obstical and we didn't already published this while in the radius
                if distance < self.min_distance_obstacle and self.obstacle_list[obstical_name]:
                    self.obstacle_list[obstical_name] = False
                    logger_msg = loggerMessage()
                    logger_msg.time_stamp = time_Stemp
                    obstical_name=obstical_name.replace("free_marker_","")
                    logger_msg.object_name = "Obstacle {0} ,{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}".format(obstical_name,"","","","",distance,"","","",obs_pose.x,obs_pose.y,obs_pose.z,robot_pos.x,robot_pos.y,robot_pos.z)
                    logger_msg.distance = 0.0
                    self.publisher.publish(logger_msg)
                # if we are not near an obstacle anymore set to true so we will publish the next time we are near an obstacle
                elif distance > self.min_distance_obstacle:
                    self.obstacle_list[obstical_name] = True
            except:
                pass

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
