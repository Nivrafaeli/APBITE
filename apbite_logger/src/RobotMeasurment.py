#!/usr/bin/python

import rospy
import math
from apbite_logger.msg import loggerMessage
from std_msgs.msg import String
from apbite.msg import KnowledgeMsg

import rospy
from apbite_logger.msg import loggerMessage
from geometry_msgs.msg import Transform
import tf
from RealPositions import *
WAITING_DURATION=1.0


class robotLocalizationListener(object):
    def __init__(self, robot_name):
        self.robot_name = robot_name
        self.agentTransform=Transform()
        topic_name = "%s/localization" % robot_name
        self.listener = rospy.Subscriber(topic_name, Transform, self.localization_callback)


    def localization_callback(self, msg):
        try:
            print str(msg)
            self.agentTransform.translation = msg.translation
            self.agentTransform.rotation= msg.rotation
        except ValueError:
            rospy.logdebug("Can not localize robot %s" % self.robot_name)
            return

    def getTransform(self):
        return self.agentTransform

class robotMeasurmentPublisher(object):
    def __init__(self, publish_topic_name, robot_name):
        self.robot_name = robot_name
        self.knowladge_topic_name = str.format('/bite/{0}/knowledge_update', self.robot_name)
        self.publisher = rospy.Publisher(publish_topic_name, loggerMessage, queue_size=100)
        self.obstacle_timer = rospy.Time().now()
        self.target_timer = rospy.Time().now()
        self.publish_target = True
        self.publish_obstacle = True
        self.AgentLocalisation=robotLocalizationListener(self.robot_name)
        self.realPositions = realPositions()
        self.tflistener = tf.TransformListener()
        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            rospy.wait_for_message(self.knowladge_topic_name, KnowledgeMsg)
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.knowladge_topic_name, KnowledgeMsg, self.knowledge_callback)

        self.agent_transform=self.AgentLocalisation.getTransform()

    def GetSuspectedTransform(self,marker):
        t1=Transform()
        markerFrame="4x4_"+marker
        mapFrame="map"
        a = self.tflistener.waitForTransform(mapFrame, markerFrame, rospy.Time(), rospy.Duration(WAITING_DURATION))
        if (a == None):
            now = rospy.Time.now()
            transform = self.tflistener.lookupTransform(mapFrame, markerFrame, rospy.Time(0))
            if transform is not None:
                t1=transform
        return t1

    def PositionToString(self,position):
        return ","+str(position.x)+","+str(position.y)+","+str(position.z)

    def calcDist(self,a,b):
        return math.sqrt((a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2)

    def knowledge_callback(self, msg):
        data = msg.data.split()
        time_stamp = rospy.Time.now()
        '''
        # if you already published that you saw a target but it was over 0.5 sec ago then we publish again
        if not self.publish_target and rospy.Time().now() - self.target_timer > rospy.Duration(0.5):
            self.publish_target = True
        '''
        # if the robot published that he reached a target and we didn't already published in the last 5 seconds
        # then we publish to the result measurment topic
        #if data[0].strip() == "ReachedToTarget" and data[1].strip() == "True" and self.publish_target:
        if data[0].strip() == "TargetReached":
            self.publish_target = False
            self.target_timer = rospy.Time.now()
            logger_msg = loggerMessage()
            logger_msg.time_stamp = time_stamp
            target_num, distance_str = data[1].strip().split(",")
            targetRealPosition = self.realPositions.getPositionOf("target"+target_num)
            RobotPosition = self.realPositions.getPositionOf(self.robot_name)


            #opening="Target Reached"+data[1].strip()+","
            opening = "Target Reached" + target_num + ","
            second = "," + ","+ ","+ distance_str+","
            realDistance_str = str(self.calcDist(targetRealPosition, RobotPosition)) + ","
            theird = "," + ","
            targetLocation_str = self.PositionToString(targetRealPosition)
            robotLocation_str = self.PositionToString(RobotPosition)

            logger_msg.object_name = opening+second+realDistance_str+theird+targetLocation_str+robotLocation_str
            logger_msg.distance = 1.0
            self.publisher.publish(logger_msg)

        # if you already published that you saw an obstacle but it was over 0.5 sec ago then we publish again
        if not self.publish_obstacle and rospy.Time().now() - self.obstacle_timer > rospy.Duration(0.5):
            self.publish_obstacle = True

        # if the robot saw an obstacle and we didn't already published in the last 5 seconds
        # then we publish to the result measurment topic

        obstacle_list=["52","59","70","73","16","17","18","19","20","21"]
        for obs in obstacle_list:
            if data[0].strip() == "Obstacle_"+ obs and self.publish_obstacle:
                #try:
                logger_msg = loggerMessage()
                logger_msg.time_stamp = time_stamp
                Suspectedtransform = self.GetSuspectedTransform(obs)
                (susTrans, rot) = Suspectedtransform

                opening="myObstacle " + obs +","
                robot2obs_andDistance_str=str(data[1].strip())+","
                markerPosition=self.realPositions.getPositionOf("free_marker_" + str(obs))
                RobotPosition=self.realPositions.getPositionOf(self.robot_name)
                ObsLocation_str = self.PositionToString(markerPosition)
                robotLocation_str=self.PositionToString(RobotPosition)
                realDistance_str=str(self.calcDist(markerPosition,RobotPosition))+","
                SuspectedTrans_str = str(susTrans[0]) + "," + str(susTrans[1]) + "," + str(susTrans[2])

                logger_msg.object_name =opening +robot2obs_andDistance_str+realDistance_str+SuspectedTrans_str+ObsLocation_str+robotLocation_str
                logger_msg.distance = 1.0
                self.publisher.publish(logger_msg)
                #except:
                 #   pass


if __name__=="__main__":
    rospy.init_node("robot_measurment")
    robot_name = rospy.get_param("~robot_name")
    topic_name = "results_%s" % robot_name
    robotMeasurmentPublisher(topic_name, robot_name)
    rospy.spin()
