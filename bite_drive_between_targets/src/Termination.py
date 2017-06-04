import rospy
from BehaviorBase import BehaviorBase

class Termination(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):

        self.update('ReachedUpdated', False)
        print "*** Termination ***"