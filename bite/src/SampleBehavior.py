import rospy
from BehaviorBase import BehaviorBase

class SampleBehavior(BehaviorBase):

    def onReceive(self, key, value):
        print str.format('I received that {0} is {1}', key, value)

    def run(self):
        print 'Updating the knowledgebase'
        self.update('Key', 'Value')
        print 'Getting knowledge of "Key"'
        value = self.getKnowledge('Key')
        print str.format('Got {0}', value)
        print 'Broadcasting to r0 and r1'
        self.broadcast(['r0', 'r1'], 'Key', value)
