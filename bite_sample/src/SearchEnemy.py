import rospy
from BehaviorBase import BehaviorBase
from random import randrange

class SearchEnemy(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        while (True):
            x = randrange(3, 14)
            print str.format('In {0} seconds going to find enemy', x)
            rospy.sleep(x)
            if not self.getKnowledge('Attack') == 'True':
                self.update('EnemyFound', self.robotName)
            else:
                break
