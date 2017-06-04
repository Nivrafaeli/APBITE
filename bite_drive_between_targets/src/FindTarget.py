import rospy
import math
import tf
from BehaviorBase import BehaviorBase
from skills import *


class FindTarget(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        #self.update('AllRobotsReachedDestination', False)
        #self.update('ReachedDestination', False)
        self.update('TargetLocation', 'Updating')
        print "*** AP FindTarget activated ***"
        while not rospy.is_shutdown():
            pass
            #(found, trans, rot) = getTargetLocation("lizi_1", 1,trans=None, rot=None)
            #if found:
            #    print "I found it in:" +str(trans) +str(rot)
