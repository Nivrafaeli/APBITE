import rospy
from std_msgs.msg import String
from bite.msg import InformMsg
from bite.srv import GetKnowledge

class BehaviorBase:
    def __init__(self, robotName, behaviorName, params):
        self.robotName = robotName
        self.behaviorName = behaviorName
        self.params = params

        self.broadcastPublisher = rospy.Publisher('/bite/broadcast', InformMsg, queue_size=100)
        self.knowledgeUpdatePublisher = rospy.Publisher(str.format('/bite/{0}/knowledge_update', robotName), String, queue_size=100)
        rospy.Subscriber(str.format('/bite/{0}/behavior_update', robotName), String, self.receiveCallback)
        rospy.Subscriber(str.format('/bite/{0}/terminate', robotName), String, self.terminationCallback)

        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)

    def receiveCallback(self, data):
        (key, value) = data.data.split()
        self.onReceive(key, value)

    def terminationCallback(self, data):
        if data.data == self.behaviorName:
            rospy.signal_shutdown('Done')

    def update(self, key, value):
        self.knowledgeUpdatePublisher.publish(str.format('{0} {1}', key, value))

    def broadcast(self, to, key, value):
        self.broadcastPublisher.publish(self.robotName, to, str.format('INFORM {0} {1}', key, value))

    def getKnowledge(self, key):
        return self.getKnowledgeClient(key).value

    #################################################
    # Default methods to be overriden by inhertiors #
    #################################################
    def onReceive(self, key, value): pass

    def run(self): pass

