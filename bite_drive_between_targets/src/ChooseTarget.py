import rospy
from BehaviorBase import BehaviorBase


class ChooseTarget(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):
        #Cancel termination condition of previous behaviour
        self.update('ReachedToTarget', False)
        self.update('ReachedUpdated', False)

        print "*** ChooseTarget ***"
        #Search for the next target


        currTarget = int(self.getKnowledge('CurrentTarget'))
        if currTarget ==0:
            self.update('CurrentTarget',"1")
        else:
            self.update('CurrentTarget', str(int(self.getKnowledge('CurrentTarget'))+1))

        # Termination
        self.update('TargetChosen', True)

