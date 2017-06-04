import rospy
from BehaviorBase import BehaviorBase
from random import randrange

class MoveToDestination(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        x = randrange(3, 14)
        print str.format('In {0} seconds reaching cell', x)
        rospy.sleep(x)
        self.update('ReachedDestination', self.robotName)
