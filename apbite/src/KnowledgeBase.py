#!/usr/bin/env python

import rospy
from rospkg import RosPack
from sys import argv
from apbite.msg import *
from apbite.srv import *
from std_msgs.msg import String
from DependenciesParser import DependenciesParser

class KnowledgeBase:
    def __init__(self, robotName, dependencies):
        self.robotName = robotName
        self.dependencies = dependencies
        self.knowledge = {'Team':robotName}
        self.LastUpdateTime = {'Team':rospy.Time.now()}
        self.LastChangeTime = {'Team': rospy.Time.now()}
        #self.LastUpdateTime = {}
        self.behaviorsToRobotsMapping = {}

        self.broadcastPublisher = rospy.Publisher('/bite/broadcast', InformMsg, queue_size=100)
        self.behaviorUpdatePublisher = rospy.Publisher(str.format('/bite/{0}/behavior_update', self.robotName), String, queue_size=100)

        rospy.Subscriber('/bite/broadcast', InformMsg, self.receiveCallback)
        rospy.Subscriber(str.format('/bite/{0}/knowledge_update', self.robotName), KnowledgeMsg, self.updateCallback)

        rospy.Service(str.format('/bite/{0}/get_knowledge', self.robotName), GetKnowledge, self.getKnowledge)

        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        rospy.Service(str.format('/bite/{0}/get_LastUpdateTime', self.robotName), GetLastUpdateTimeStr, self.getLastUpdateTime)
        rospy.Service(str.format('/bite/{0}/get_LastChangeTime', self.robotName), GetLastChangeTime, self.getLastChangeTime)
        # ***********************************
        #  Active Perception block ends     #
        # ***********************************

    # Gets a specific knowledge from the knowledgebase
    def getKnowledge(self, req):
        key = req.key
        if not key in self.knowledge:
            # The default value is False
            return GetKnowledgeResponse('False')
        return GetKnowledgeResponse(self.knowledge[key])

    # ***********************************
    #  Active Perception block starts   #
    # ***********************************

    def getLastUpdateTime(self, req):
        key = req.key
        if not key in self.LastUpdateTime:
            # The default value is False
            return GetLastUpdateTimeStrResponse('False')
        ans=str(self.LastUpdateTime[key].to_sec())
        return GetLastUpdateTimeStrResponse(ans)

    def getLastChangeTime(self, req):
        key = req.key
        if not key in self.LastChangeTime:
            # The default value is False
            return GetLastChangeTimeResponse('False')
        return GetLastChangeTimeResponse(self.LastChangeTime[key])

    # ***********************************
    #  Active Perception block ends     #
    # ***********************************

    # Updates the knowledgebase of the specific robot
    def updateCallback(self, msg):
        data = msg.data.split()
        self.updateAndInform(self.robotName, data[0], data[1])

    # Receives information from the broadcast channel
    def receiveCallback(self, msg):
        # Updates the team members
        if not msg.from_ in self.knowledge['Team'].split(','):
            self.knowledge['Team'] += str.format(',{0}', msg.from_)

        data = msg.data.split()
        msgType = data[0]
        if self.robotName in msg.to:
            if msgType == "INFORM":
                self.updateAndInform(msg.from_, data[1], data[2])

            elif msgType == "STRATING":
                behaviorName = data[1]
                if behaviorName in self.behaviorsToRobotsMapping:
                    # Updates the behaviors to robots dictionary
                    if not msg.from_ in self.behaviorsToRobotsMapping[behaviorName]:
                        self.behaviorsToRobotsMapping[behaviorName].append(msg.from_)
                # Creates a key value pair with the behavior name as key and the value as a list
                else:
                    self.behaviorsToRobotsMapping[behaviorName] = [msg.from_]
                print str.format("Robots running {0}: {1}", behaviorName, self.behaviorsToRobotsMapping[behaviorName])

            elif msgType == "TERMINATING":
                behaviorName = data[1]
                # Removes the robot form the dictionary
                if behaviorName in self.behaviorsToRobotsMapping and msg.from_ in self.behaviorsToRobotsMapping[behaviorName]:
                    self.behaviorsToRobotsMapping[behaviorName].remove(msg.from_)
                    print str.format('Removed {0} from behavior: {1}', msg.from_, behaviorName)
                    # If no robot is running that behavior, delete entry
                    if self.behaviorsToRobotsMapping[behaviorName] == []:
                        del self.behaviorsToRobotsMapping[behaviorName]
                        print str.format('Deleted entry {0}', behaviorName)

    # Updates the knowledgebase and informs the relevant robots if needed
    def updateAndInform(self, msgFrom, key, value):


        # Informs the robot itself about the knowledge
        self.behaviorUpdatePublisher.publish(str.format('{0} {1}', key, value))
        self.LastUpdateTime[key] = rospy.Time.now()

        # DEBUGGING
        if key == "ObstacleOnTheWay" or key == "KnowsTargetLocation" or key == "CameraUp" or key == "CameraDown":  # key=="ObstacleOnTheWay_time" or key=="KnowsTargetLocation_time" or :
            #print str.format('************New knowledge*********:')
            print str.format('{0}:{1}, LastUpdate={2}', key, value, self.LastUpdateTime[key].to_sec())
        # DEBUGGING

        if key in self.knowledge and self.knowledge[key] == value:
            # Already knew about this knowledge
            return

        self.knowledge[key] = value
        self.LastChangeTime[key] = rospy.Time.now()
        #print str.format('New knowledge base: {0}', self.knowledge)




        if key in self.dependencies:
            # Inform the rest of the robots
            behaviorsList = self.dependencies[key]
            robotsList = []
            # Getting all the robots that use given data
            for behavior in behaviorsList:
                if behavior in self.behaviorsToRobotsMapping:
                    robotsList.extend([robot for robot in self.behaviorsToRobotsMapping[behavior] if robot not in robotsList])

            # Not informing the robot that sent us the message
            if msgFrom in robotsList:
                robotsList.remove(msgFrom)

            # If there are any robots besides the current robot that needs the data we broadcast it
            if not robotsList == []:
                print str.format('Informing {0} that {1} is {2}', robotsList, key, value)
                self.broadcastPublisher.publish(self.robotName, robotsList, str.format('INFORM {0} {1}', key, value))

if __name__ == '__main__':
    if len(argv) < 3:
        raise Exception('No package or robot names given')

    packageName = str(argv[1])
    robotName = str(argv[2])

    print 'Initiating the Knowledge Base node'
    rospy.init_node(str.format('bite_{0}_knowledgebase_node', robotName.lower()))

    # Getting the Behavior dependencies
    packagePath = RosPack().get_path(packageName)
    dependencies = DependenciesParser(str.format('{0}/dependencies.xml', packagePath)).getBehaviorDependencies()
    KnowledgeBase(robotName, dependencies)

    print 'Knowledgebase ready'
    rospy.spin()
