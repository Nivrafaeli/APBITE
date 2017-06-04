import rospy
from BehaviorBase import BehaviorBase

class Initialize(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)
        self.update('EnemyDestroyed', False)
        self.update('Attack', False)
        self.robotsDone = 0

    def onReceive(self, key, value):
        if key == 'ReachedDestination':
            self.robotsDone += 1
            if self.robotsDone == self.getKnowledge('Team').count(',') + 1:
                self.update('AllRobotsReachedDestination', True)
