import rospy
from BehaviorBase import BehaviorBase
from random import randrange

class AttackFromSide(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        print str.format('Attacking from the {0}', self.params[0])
        x = randrange(3, 24)
        print str.format('In {0} seconds going to destroy enemy', x)
        rospy.sleep(x)
        if self.getKnowledge('EnemyDestroyed') == 'False':
            if self.getKnowledge('OddNumberOfEnemiesDestroyed') == 'False':
                self.update('OddNumberOfEnemiesDestroyed', True)
            else:
                self.update('OddNumberOfEnemiesDestroyed', False)
            self.update('EnemyDestroyed', True)
