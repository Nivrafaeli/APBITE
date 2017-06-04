import rospy
from BehaviorBase import BehaviorBase

class Attack(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        self.update('AllRobotsReachedDestination', False)
        self.update('ReachedDestination', False)

