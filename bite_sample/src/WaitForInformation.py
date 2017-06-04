import rospy
from BehaviorBase import BehaviorBase

class WaitForInformation(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)
        self.enemiesFound = 0

    def onReceive(self, key, value):
        if key == 'EnemyFound':
            print str.format('I heard that {0} found an enemy', value)
            self.enemiesFound += 1
            print str.format('Enemies found: {0}', self.enemiesFound)
            if self.enemiesFound == 5:
                self.update('Attack', True)
