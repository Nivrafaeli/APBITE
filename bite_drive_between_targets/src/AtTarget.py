import rospy
from BehaviorBase import BehaviorBase

class AtTarget(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)

    def run(self):

        print "*** AtTarget ***"
        # Cancel termination condition of previous behaviour
        self.update('ReachedToTarget', False)

        old_num=self.getKnowledge('NumberOfTargets')
        print old_num
        current_number_of_targets= int(old_num)-1
        if current_number_of_targets == 0:
            self.update('ThereAreTargets', False)
            self.update('ThereAreNoTargets', True)
        else:
            self.update('NumberOfTargets', str(current_number_of_targets))
        self.update('ReachedUpdated', True)
        #if there are no more targets go to terminal state