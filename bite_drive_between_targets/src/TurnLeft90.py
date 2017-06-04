import rospy
from BehaviorBase import BehaviorBase
from skills import *
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Transform
import math

from std_msgs.msg import Float64
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

class TurnLeft90(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        #
        self.robotName = robotName
        rospy.sleep(0.5)
        self.command_pub = rospy.Publisher(str.format('/{0}/diff_driver/command', self.robotName), Twist, queue_size=10)
        self.ROTATE_SPEED_MPS = 0.6
        self.SLOW_ROTATE_SPEED_MPS = 0.2
        self.trans = None
        self.rot = None
        self.found = False

        self.realPositions = realPositions()

    def run(self):
        #Cancel termination condition of previous behaviour
        self.update('TargetChosen', False)
        self.update('SearchingTarget', True)
        print "*** SearchTarget ***"


        currTarget = int(self.getKnowledge('CurrentTarget'))
        RobotPosition=None
        while not rospy.is_shutdown() and RobotPosition is None:
            RobotPosition = self.realPositions.getPoseOf(self.robotName)
        q = RobotPosition.orientation
        Currentyaw = math.atan2(2.0 * (q.x * q.y + q.w * q.z), q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);
        turnYaw=1.5707
        destYaw=Currentyaw+turnYaw


        #currentDirection=RobotPosition.orientation.z
        #turn=0.7071
        #destDirection=currentDirection+turn

        #Rotation message
        rotate_msg = Twist()  # The default constructor will set all commands to 0
        rotate_msg.angular.z = self.ROTATE_SPEED_MPS
        aimed=False


        if currTarget==1:
            aimed = True
        i=0
        while not rospy.is_shutdown() and not aimed:
            i=i+1
            self.command_pub.publish(rotate_msg)
            RobotPosition = self.realPositions.getPoseOf(self.robotName)
            q=RobotPosition.orientation

            Currentyaw = math.atan2(2.0 * (q.x * q.y + q.w * q.z), q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);

            #print "Destination: " + str(destDirection)
            #print "currentDirection: " + str(currentDirection)
            currentDirection = RobotPosition.orientation.z
            if i%500==0:
                rospy.logerr("Robot yaw {0}".format(str(Currentyaw)))
            print ("\n")
            if Currentyaw >= destYaw or Currentyaw<0:
                while not rospy.is_shutdown() and not aimed:
                    i=i+1
                    rotate_msg.angular.z = -self.SLOW_ROTATE_SPEED_MPS
                    if i % 500 == 0:
                        rospy.logerr("Robot yaw {0}".format(str(Currentyaw)))
                    self.command_pub.publish(rotate_msg)
                    #currentDirection = self.realPositions.getPoseOf(self.robotName).orientation.z
                    RobotPosition = self.realPositions.getPoseOf(self.robotName)
                    q = RobotPosition.orientation
                    Currentyaw = math.atan2(2.0 * (q.x * q.y + q.w * q.z),
                                            q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);

                    if Currentyaw  <= destYaw:
                        aimed=True


        rospy.logerr("{0}: Aimed to target number {1}".format(self.behaviorName,currTarget))
        msg = Twist()  # The default constructor will set all commands to 0
        msg.angular.z = 0
        self.command_pub.publish(msg)

        # Termination
        self.update('Target_Found', True)
        self.update('SearchingTarget', False)