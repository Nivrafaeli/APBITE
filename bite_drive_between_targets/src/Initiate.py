import rospy
from BehaviorBase import BehaviorBase

class Initiate(BehaviorBase):

    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)
        #update initial beliefs, targets details
        self.update('ThereAreTargets', True)
        self.update('NumberOfTargets', 3)
        self.update('ObstacleFound', False)
        self.update('CurrentTarget', 0)

        self.update('NumberOfObstacles', 0)
        self.update('DefusedObstacle', 0)
        self.update('CameraDown', 'True')
        self.update('UsingCamera', 'False')

        '''self.update('KnowsTargetLocation', 'False')
        self.update('KnowsTargetLocation_time', rospy.Time.now())
        self.update('ObstacleOnTheWay', 'False')
        self.update('ObstacleOnTheWay_time', rospy.Time.now())
'''

    def run(self):

        print "*** Initiate *** "
        #Termination
        self.update('AllReady', True)