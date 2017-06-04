import rospy
from BehaviorBase import BehaviorBase

class LookForObstacle(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        #self.update('AllRobotsReachedDestination', False)
        #self.update('ReachedDestination', False)
        print "*** LookForObstacle ***"
        #When the camera is looking down the first assumption is that there are no obstacles,
        #'go forward' will update if there are obstacles

