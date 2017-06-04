import rospy
from BehaviorBase import BehaviorBase
from skills import *
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Transform
import math

from std_msgs.msg import Float64

class SearchTarget(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        #
        self.robotName = robotName
        rospy.sleep(0.5)
        self.command_pub = rospy.Publisher(str.format('/{0}/diff_driver/command', self.robotName), Twist, queue_size=10)
        self.ROTATE_SPEED_MPS = 0.5
        self.SLOW_ROTATE_SPEED_MPS = 0.1
        self.trans = None
        self.rot = None
        self.found = False

    def callback(self, msg):
        if msg == Transform():
            self.found = False
        else:
            self.trans = msg.translation
            self.rot = msg.rotation
            self.found = True

    def run(self):
        #Cancel termination condition of previous behaviour
        self.update('TargetChosen', False)
        self.update('SearchingTarget', True)
        print "*** SearchTarget ***"


        currTarget = int(self.getKnowledge('CurrentTarget'))

        #Starting a thread that publishes the target transformation from the robot (using different thread for each marker)
        report_topic = str.format('/{0}/transformation/{1}', self.robotName, currTarget)
        directions = ["front", "right", "rear", "top", "left"]
        markerNames=["target"+str(currTarget)+"_"+direction+"_base_link" for direction in directions]
        reporter = ReportLocation(self.robotName, currTarget, report_topic,markerNames)
        reporter.start()
        rospy.wait_for_message(report_topic,Transform)

        #Listening to that topic
        listener = rospy.Subscriber(report_topic, Transform, self.callback, queue_size=10)

        #Rotation message
        rotate_msg = Twist()  # The default constructor will set all commands to 0
        rotate_msg.angular.z = self.ROTATE_SPEED_MPS
        aimed=False
        while not rospy.is_shutdown() and not self.found and not aimed:
            self.command_pub.publish(rotate_msg)
            # self.ROTATE_SPEED_MPS = self.ROTATE_SPEED_MPS*-1
            if self.found:
                #print "I found it in:" + str(self.trans) + str(self.rot)

                while ((not rospy.is_shutdown()) and (self.found) and (not self.trans.y ** 2 < 0.1) ):
                    if self.trans.y < 0:
                        rotate_msg.angular.z = -self.SLOW_ROTATE_SPEED_MPS
                    else:
                        rotate_msg.angular.z = self.SLOW_ROTATE_SPEED_MPS
                    self.command_pub.publish(rotate_msg)

                    #print "Target is in x:{0} y:{1} z:{2}".format(str(self.trans.x), str(self.trans.y), str(self.trans.z))
                    if self.found:
                        if  self.trans.y ** 2 < 0.1:
                            #print "new trans.y:" + str(self.trans.y)
                            aimed=True

        #msg.angular.z = self.SLOW_ROTATE_SPEED_MPS
        rospy.logerr("{0}: Aimed to target number {1}".format(self.behaviorName,currTarget))
        msg = Twist()  # The default constructor will set all commands to 0
        msg.angular.z = 0
        self.command_pub.publish(msg)

        # Termination
        self.update('Target_Found', True)
        self.update('SearchingTarget', False)