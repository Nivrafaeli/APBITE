#!/usr/bin/python

import rospy
import math
from BehaviorBase import BehaviorBase
from geometry_msgs.msg import Twist
from skills import *
from geometry_msgs.msg import Transform
from std_msgs.msg import Float64
import tf
import rospy
from gazebo_msgs.msg import ModelStates
import sys



class realPositions(object):

    GAZEBO_TOPIC_NAME = "/gazebo/model_states"

    def __init__(self):
        self.locations = {}
        self.last_update_time = rospy.Time.now()
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
        self.last_update_time = rospy.Time.now()

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

    def getTimedPosition(self, item):
        position = self.getPositionOf(item)
        return position, self.last_update_time

    def getLocations(self):
        try:
            return self.locations
        except:
            return None


class GoToTarget(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)
        #In multirobot i will have to take care of the namespaces
        self.command_pub = rospy.Publisher(str.format('/lizi_1/diff_driver/command', robotName), Twist, queue_size=10)
        self.FORWARD_SPEED_MPS = 0.2

        self.realPositions=realPositions()

        #My location
        self.mytrans=None
        self.myrot = None
        self.mylocupdated = False

        #Targets
        self.trans = None
        self.rot = None
        self.found = False

        #obstacles
        self.trans_52 = None
        self.rot_52 = None
        self.found_52 = False
        self.trans_59 = None
        self.rot_59 = None
        self.found_59 = False
        self.trans_70 = None
        self.rot_70 = None
        self.found_70 = False
        self.trans_73 = None
        self.rot_73 = None
        self.found_73 = False
        self.trans_16 = None
        self.rot_16 = None
        self.found_16 = False
        self.trans_17 = None
        self.rot_17 = None
        self.found_17 = False
        self.trans_18 = None
        self.rot_18 = None
        self.found_18 = False
        self.trans_19 = None
        self.rot_19 = None
        self.found_19 = False
        self.trans_20 = None
        self.rot_20 = None
        self.found_20 = False
        self.trans_21 = None
        self.rot_21 = None
        self.found_21 = False

        self.found_52_print=True
        self.found_59_print = True
        self.found_70_print = True
        self.found_73_print = True
        self.found_16_print = True
        self.found_17_print = True
        self.found_18_print = True
        self.found_19_print = True
        self.found_20_print = True
        self.found_21_print = True

        self.timer = rospy.Time().now()

    #Mylocation
    def callback_mylocation(self, msg):
        if msg == Transform():
            self.mylocupdated = False
        else:
            self.mytrans = msg.translation
            self.myrot = msg.rotation
            self.mylocupdated = True

    #target
    def callback(self, msg):
        if msg == Transform():
            self.found = False
        else:
            self.trans = msg.translation
            self.rot = msg.rotation
            self.found = True

    # Obstacles
    def callback_52(self, msg):
        if msg == Transform():
            self.found_52 = False
        else:
            self.trans_52 = msg.translation
            self.rot_52 = msg.rotation
            self.found_52 = True

    def callback_59(self, msg):
        if msg == Transform():
            self.found_59 = False
        else:
            self.trans_59 = msg.translation
            self.rot_59 = msg.rotation
            self.found_59 = True

    def callback_70(self, msg):
        if msg == Transform():
            self.found_70 = False
        else:
            self.trans_70 = msg.translation
            self.rot_70 = msg.rotation
            self.found_70 = True

    def callback_73(self, msg):
        if msg == Transform():
            self.found_73 = False
        else:
            self.trans_73 = msg.translation
            self.rot_73 = msg.rotation
            self.found_73 = True

    def callback_16(self, msg):
        if msg == Transform():
            self.found_16 = False
        else:
            self.trans_16 = msg.translation
            self.rot_16 = msg.rotation
            self.found_16 = True

    def callback_17(self, msg):
        if msg == Transform():
            self.found_17 = False
        else:
            self.trans_17 = msg.translation
            self.rot_17 = msg.rotation
            self.found_17 = True

    def callback_18(self, msg):
        if msg == Transform():
            self.found_18 = False
        else:
            self.trans_18 = msg.translation
            self.rot_18 = msg.rotation
            self.found_18 = True

    def callback_19(self, msg):
        if msg == Transform():
            self.found_19 = False
        else:
            self.trans_19 = msg.translation
            self.rot_19 = msg.rotation
            self.found_19 = True

    def callback_20(self, msg):
        if msg == Transform():
            self.found_20 = False
        else:
            self.trans_20 = msg.translation
            self.rot_20 = msg.rotation
            self.found_20 = True

    def callback_21(self, msg):
        if msg == Transform():
            self.found_21 = False
        else:
            self.trans_21 = msg.translation
            self.rot_21 = msg.rotation
            self.found_21 = True

    def calcDistance(self,trans):
        distance = math.sqrt(trans.x ** 2 + trans.y ** 2 + trans.z ** 2)
        return distance

    def updateSupportBelief(self,bel,val):
        #This function updates beliefs only every 0.2 or more

        # bel is the beliefs name
        # val is the value we want the belief to be updated

        BelLastUpdate= self.getLastUpdateTime(bel)
        now = rospy.Time.now()
        t = 0.2
        t_secs_ago = now - rospy.Duration(t)  # Time minus Duration is a Time
        BelLastUpdate = self.getLastUpdateClient(bel).sec
        if BelLastUpdate == 'False':  # If it is unknown (never been updated)
            self.update(bel, val)
        else:  # If it is known but last updated time is longer than t
            BelValue = self.getKnowledge(bel)
            if BelValue==val:
                last_updated_time = rospy.Time.from_sec(float(BelLastUpdate))
                if last_updated_time < t_secs_ago:
                    self.update(bel, val)
            else: #If the known value is different
                self.update(bel, val)

    def run(self):
        print "*** GoToTarget ***"
        # Cancel termination condition of previous behaviour
        self.update('Target_Found', False)
        distance=100
        currTarget = int(self.getKnowledge('CurrentTarget'))

        # My loaction topic
        report_topic_mylocation = str.format('/{0}/transformation/{1}', self.robotName, "Mylocation")
        reporter_mylocation = ReportAgentsLocation(self.robotName, report_topic_mylocation)
        reporter_mylocation.start()
        rospy.wait_for_message(report_topic_mylocation, Transform)
        listener_location = rospy.Subscriber(report_topic_mylocation, Transform, self.callback_mylocation, queue_size=10)


        #Target topic
        report_topic = str.format('/{0}/transformation/{1}', self.robotName, currTarget)
        directions = ["front", "right", "rear", "top", "left"]
        markerNames = ["target" + str(currTarget) + "_" + direction + "_base_link" for direction in directions]
        reporter = ReportLocation(self.robotName, currTarget, report_topic, markerNames)
        reporter.start()
        rospy.wait_for_message(report_topic, Transform)
        listener = rospy.Subscriber(report_topic, Transform, self.callback, queue_size=10)
        rospy.logerr("Target topic")

        #Start obstacle finder _52
        marker_name="52"
        report_topic_52 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_"+str(marker_name)]
        reporter_52 = ReportLocation(self.robotName, marker_name, report_topic_52, markerNames)
        reporter_52.start()
        rospy.wait_for_message(report_topic_52, Transform)
        listener_52 = rospy.Subscriber(report_topic_52, Transform, self.callback_52, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _59
        marker_name = "59"
        report_topic_59 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_59 = ReportLocation(self.robotName, marker_name, report_topic_59, markerNames)
        reporter_59.start()
        rospy.wait_for_message(report_topic_59, Transform)
        listener_59 = rospy.Subscriber(report_topic_59, Transform, self.callback_59, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _70
        marker_name = "70"
        report_topic_70 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_70 = ReportLocation(self.robotName, marker_name, report_topic_70, markerNames)
        reporter_70.start()
        rospy.wait_for_message(report_topic_70, Transform)
        listener_70 = rospy.Subscriber(report_topic_70, Transform, self.callback_70, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _73
        marker_name = "73"
        report_topic_73 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_73 = ReportLocation(self.robotName, marker_name, report_topic_73, markerNames)
        reporter_73.start()
        rospy.wait_for_message(report_topic_73, Transform)
        listener_73 = rospy.Subscriber(report_topic_73, Transform, self.callback_73, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _16
        marker_name = "16"
        report_topic_16 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_16 = ReportLocation(self.robotName, marker_name, report_topic_16, markerNames)
        reporter_16.start()
        rospy.wait_for_message(report_topic_16, Transform)
        listener_16 = rospy.Subscriber(report_topic_16, Transform, self.callback_16, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _17
        marker_name = "17"
        report_topic_17 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_17 = ReportLocation(self.robotName, marker_name, report_topic_17, markerNames)
        reporter_17.start()
        rospy.wait_for_message(report_topic_17, Transform)
        listener_17 = rospy.Subscriber(report_topic_17, Transform, self.callback_17, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _18
        marker_name = "18"
        report_topic_18 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_18 = ReportLocation(self.robotName, marker_name, report_topic_18, markerNames)
        reporter_18.start()
        rospy.wait_for_message(report_topic_18, Transform)
        listener_18 = rospy.Subscriber(report_topic_18, Transform, self.callback_18, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _19
        marker_name = "19"
        report_topic_19 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_19 = ReportLocation(self.robotName, marker_name, report_topic_19, markerNames)
        reporter_19.start()
        rospy.wait_for_message(report_topic_19, Transform)
        listener_19 = rospy.Subscriber(report_topic_19, Transform, self.callback_19, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _20
        marker_name = "20"
        report_topic_20 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_20 = ReportLocation(self.robotName, marker_name, report_topic_20, markerNames)
        reporter_20.start()
        rospy.wait_for_message(report_topic_20, Transform)
        listener_20 = rospy.Subscriber(report_topic_20, Transform, self.callback_20, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        # Start obstacle finder _21
        marker_name = "21"
        report_topic_21 = str.format('/{0}/transformation/{1}', self.robotName, marker_name)
        markerNames = ["4x4_" + str(marker_name)]
        reporter_21 = ReportLocation(self.robotName, marker_name, report_topic_21, markerNames)
        reporter_21.start()
        rospy.wait_for_message(report_topic_21, Transform)
        listener_21 = rospy.Subscriber(report_topic_21, Transform, self.callback_21, queue_size=10)
        rospy.logerr("Obstacle finder {0}".format(str(marker_name)))
        print "***********************************************start driving**************************************"
        i=0
        last_update=0
        self.update('Driving', True)
        while not rospy.is_shutdown() and not distance<2.0:
            self.move_forward()
            #look for targets
            foundTargetAndDistanceIsOK = False
            """
            #************************************************delete****
            real_targetPosition, real_update_time = self.realPositions.getTimedPosition("target" + str(currTarget))
            RobotPosition, robot_update_time = self.realPositions.getTimedPosition(self.robotName)
            rospy.logwarn("*******Target real pos x={0} y={1} z={2}".format(str(real_targetPosition.x),
                                                                           str(real_targetPosition.y),
                                                                           str(real_targetPosition.z)))
            rospy.logwarn("*******Robot pos x={0} y={1} z={2}".format(str(RobotPosition.x),
                                                                     str(RobotPosition.y),
                                                                   str(RobotPosition.z)))
            rospy.logerr("*******Update times are robot: {0} and real: {1}".format(str(robot_update_time),
                                                                                   str(real_update_time)))
            # ************************************************delete****
            """
            if self.found:
                distance = math.sqrt(self.trans.x ** 2 + self.trans.y ** 2 + self.trans.z ** 2)
                if distance<2.0:
                    real_targetPosition, real_update_time = self.realPositions.getTimedPosition("target" + str(currTarget))
                    RobotPosition, robot_update_time = self.realPositions.getTimedPosition(self.robotName)
                    x = real_targetPosition.x - RobotPosition.x
                    y = real_targetPosition.y - RobotPosition.y
                    z = real_targetPosition.z - RobotPosition.z
                    real_distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)
                    self.update('TargetDistance_Real_assumed' ,str(real_distance)+"_"+str(distance))


                    if real_distance>2.5:
                        #The real distance is too far, The algorithm does not accept this as an otion
                        rospy.logerr("*******Target real pos x={0} y={1} z={2}".format(str(real_targetPosition.x),str(real_targetPosition.y),str(real_targetPosition.z)))
                        rospy.logerr("*******Robot pos x={0} y={1} z={2}".format(str(RobotPosition.x),
                                                                                       str(RobotPosition.y),
                                                                                       str(RobotPosition.z)))

                        rospy.logerr("*******REAL distance is very large {0} - cant accept".format(str(real_distance)))
                        rospy.logerr("*******Update times are robot: {0} and real: {1}".format(str(robot_update_time),
                                                                                                str(real_update_time)))
                        distance=100
                    else:
                        foundTargetAndDistanceIsOK=True

                    #foundTargetAndDistanceIsOK = True
            foundObstacle=False
            if self.found_52:
                Obstacle_dist=self.calcDistance(self.trans_52)
                if Obstacle_dist < 1.5:
                    obstacle_name="52"
                    if self.found_52_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_'+obstacle_name, str(self.trans_52.x)+","+str(self.trans_52.y)+","+str(self.trans_52.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_59:
                Obstacle_dist=self.calcDistance(self.trans_59)
                if Obstacle_dist < 1.5:
                    obstacle_name="59"
                    if self.found_59_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_59_print=False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_59.x) + "," + str(self.trans_59.y) + "," + str(self.trans_59.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_70:
                Obstacle_dist=self.calcDistance(self.trans_70)
                if Obstacle_dist < 1.5:
                    obstacle_name="70"
                    if self.found_70_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_70_print=False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_70.x) + "," + str(self.trans_70.y) + "," + str(self.trans_70.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_73:
                Obstacle_dist = self.calcDistance(self.trans_73)
                if Obstacle_dist < 1.5:
                    obstacle_name = "73"
                    if self.found_73_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_73_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_73.x) + "," + str(self.trans_73.y) + "," + str(self.trans_73.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_16:
                Obstacle_dist = self.calcDistance(self.trans_16)
                if Obstacle_dist < 1.5:
                    obstacle_name = "16"
                    if self.found_16_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_16_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_16.x) + "," + str(self.trans_16.y) + "," + str(self.trans_16.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_17:
                Obstacle_dist = self.calcDistance(self.trans_17)
                if Obstacle_dist < 1.5:
                    obstacle_name = "17"
                    if self.found_17_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_17_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_17.x) + "," + str(self.trans_17.y) + "," + str(self.trans_17.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_18:
                Obstacle_dist = self.calcDistance(self.trans_18)
                if Obstacle_dist < 1.5:
                    obstacle_name = "18"
                    if self.found_18_print:
                        #rospy.logerr( "{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_18_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_18.x) + "," + str(self.trans_18.y) + "," + str(self.trans_18.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_19:
                Obstacle_dist = self.calcDistance(self.trans_19)
                if Obstacle_dist < 1.5:
                    obstacle_name = "19"
                    if self.found_19_print:
                        #rospy.logerr( "{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_19_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_19.x) + "," + str(self.trans_19.y) + "," + str(self.trans_19.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_20:
                Obstacle_dist = self.calcDistance(self.trans_20)
                if Obstacle_dist < 1.5:
                    obstacle_name = "20"
                    if self.found_20_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_20_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_20.x) + "," + str(self.trans_20.y) + "," + str(self.trans_20.z)+","+str(Obstacle_dist))

                    foundObstacle = True

            if self.found_21:
                Obstacle_dist = self.calcDistance(self.trans_21)
                if Obstacle_dist < 1.5:
                    obstacle_name = "21"
                    if self.found_21_print:
                        #rospy.logerr("{0}: Found obstacle number {1}".format(self.behaviorName, str(obstacle_name)))
                        #self.found_21_print = False
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                        self.update('Obstacle_' + obstacle_name,
                                    str(self.trans_21.x) + "," + str(self.trans_21.y) + "," + str(self.trans_21.z)+","+str(Obstacle_dist))

                    foundObstacle = True



            #**************Updates target location only if the camera is faceing
            #Checking only 0.1 so the service getknoledge will not cost too much
            TIME2UPDATE=0.1
            now = rospy.Time.now()
            time_t_secs_ago = int(str(now - rospy.Duration(TIME2UPDATE)))
            if last_update < time_t_secs_ago:
                last_update= int(str(rospy.Time.now()))
                bel_CameraDown=self.getKnowledge('CameraDown')
                bel_CameraUp = self.getKnowledge('CameraUp')
                if bel_CameraDown == 'True':
                    # Update obsticles
                    if foundObstacle == True:
                        self.updateSupportBelief('ObstacleOnTheWay', 'True')
                    else:
                        self.updateSupportBelief('ObstacleOnTheWay', 'False')
                if bel_CameraUp == 'True':
                    if self.found and foundTargetAndDistanceIsOK:
                        self.updateSupportBelief('KnowsTargetLocation', 'True')
                    else:
                        self.updateSupportBelief('KnowsTargetLocation', 'False')


        self.stop()
        self.update('Driving', False)
        self.update('ReachedToTarget', True)
        self.update('TargetReached', str(currTarget)+","+str(round(distance,2)))

    def move_forward(self):
        msg = Twist()  # The default constructor will set all commands to 0
        msg.linear.x = self.FORWARD_SPEED_MPS
        self.command_pub.publish(msg)

    def stop(self):
        msg = Twist()  # The default constructor will set all commands to 0
        msg.linear.x = 0
        self.command_pub.publish(msg)