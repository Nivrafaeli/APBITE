import rospy
from BehaviorBase import BehaviorBase

class AtObstacle(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):

        print "*** AtObstacle ***"
        #if there are obstacles menouver to avoid, or halt