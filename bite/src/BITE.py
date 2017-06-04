#!/usr/bin/env python

import rospy
from rospkg import RosPack
from sys import argv
from Plan import Plan
from bite.srv import *
from bite.msg import *
from std_msgs.msg import String
from PlanParser import PlanParser
from roslaunch.scriptapi import ROSLaunch, Node

class BITE:
    def __init__(self, robotName, plan, team, packageName):
        self.robotName = robotName
        self.plan = plan
        self.team = team
        self.packageName = packageName
        self.runningBehaviorsStack = []
        self.behaviorsRunning = []
        self.nodesToTerminate = []
        self.readyTeam = []
    	self.roslauncher = ROSLaunch()
    	self.roslauncher.start()
        
        # Initiate publishers
        # broadcast is the topic used for broadcast messages
        self.broadcastPublisher = rospy.Publisher('/bite/broadcast', InformMsg, queue_size=100)
        self.terminateBehaviorPublisher = rospy.Publisher(str.format('/bite/{0}/terminate',self.robotName), String, queue_size=100)

        # Initiate subscribers
        # broadcast is the topic used for broadcast messages
        rospy.Subscriber('/bite/broadcast', InformMsg, self.receiveCallback)

        print 'Waiting for knowledgebase...'
        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)
        print 'Ready'

        rospy.sleep(0.5)

    #######################################################
    # Expands the running behaviors stack hierarchichally #
    #######################################################
    def expandStackHierarchically(self):
        # Initiates the current node
        currentNode = self.plan.nodes[0]
        currentTeam = self.team

        if self.runningBehaviorsStack == []:
            # Adds the first node of the plan
            print str.format('Adding node "{0}" to the stack', currentNode.nodeName)
            self.runningBehaviorsStack.append((currentNode, currentTeam, ''))
        else:
            # If the stack is not empty starting from the last behavior in the stack
            currentNode, currentTeam = self.runningBehaviorsStack[-1][0:2]
            print str.format('Starting from node "{0}"', currentNode.nodeName)

        print str.format('Hierarchical children of node "{0}" are: {1}', currentNode.nodeName, [node.nodeName for node in currentNode.hierarchicalChildren])
        while not currentNode.hierarchicalChildren == []:
            # Allocating next level of hierarchy
            result = self.allocateNextNode(currentNode, currentTeam)

            if result.node == '':
                break

            currentNode = self.plan.getNode(result.node)
            currentTeam = result.newTeam

            # Adds the node to the stack
            print str.format('Adding node "{0}" to the stack', currentNode.nodeName)
            self.runningBehaviorsStack.append((currentNode, currentTeam, result.params))

            print str.format('Hierarchical children of node "{0}" are: {1}', currentNode.nodeName, [node.nodeName for node in currentNode.hierarchicalChildren])

        self.terminateBehaviorsNotInStack()
        rospy.sleep(1)
        print 'Starting behaviors in stack'
        for (node, team, params) in self.runningBehaviorsStack:
            if not node in self.behaviorsRunning:
                print str.format('Starting behavior: {0}', node.behaviorName)
                self.startBehavior(node, params)
                # Notify other robots what behavior its starting
                self.broadcastPublisher.publish(self.robotName, self.team,  str.format('STRATING {0}', node.behaviorName))

        self.nodesToTerminate = []

    ####################################################################
    # Allocate procedure for next node. Including team synchronization #
    ####################################################################
    def allocateNextNode(self, currentNode, currentTeam):
        filteredChildren = self.filterByPreConds(currentNode.hierarchicalChildren)
        print str.format('Next behaviors that their preconditions are true: {0}', [node.nodeName for node in filteredChildren])

        # Set the right allocate method for the current node
        print str.format('Node\'s allocate method is: "{0}"', currentNode.allocateMethod)
        allocateServiceName = str.format('/bite/{0}/{1}', self.robotName, currentNode.allocateMethod)
        rospy.wait_for_service(allocateServiceName)
        allocateClient = rospy.ServiceProxy(allocateServiceName, Allocate)

        if len(currentTeam) > 1:
            # Inform the rest of the team that preconditions of these behaviors are true
            print str.format('Informing the rest of the team: {0}', currentTeam)
            for node in filteredChildren:
                for preCond in node.preConds:
                    self.broadcastPublisher.publish(self.robotName, currentTeam, str.format('INFORM {0} {1}', preCond, True))

            # Sync with team
            print str.format('Waiting for team: {0}', currentTeam)
            self.waitForTeam(currentTeam)

            # Checks again after received information from other robots
            filteredChildren = self.filterByPreConds(currentNode.hierarchicalChildren)

            # Sleeps to make sure all the team gets here
            rospy.sleep(1)

        if (filteredChildren == []):
            # None of the nodes fit their preconditions
            return AllocateResponse('', [], '')
        # Calls allocate
        return allocateClient([child.nodeName for child in filteredChildren], currentTeam)

    ##############################################
    # Filters given nodes by their preconditions #
    ##############################################
    #******************************************************Should add ACTIVE PERCEPTION for pre-conditions here*****
    def filterByPreConds(self, nodes):
        filteredNodes = []
        
        # Iterates over all the given nodes
        for node in nodes:
            shouldAddNode = True
            for preCond in node.preConds:
                if not self.getKnowledgeClient(preCond).value == 'True':
                    # One of the preconds isn't true - not adding the node
                    shouldAddNode = False
                    break
            if shouldAddNode:
                filteredNodes.append(node)

        return filteredNodes

    ##############################
    # Waits for rest of the team #
    ##############################
    def waitForTeam(self, currentTeam):
        allTeamReady = False
        self.readyTeam = []
        while not allTeamReady:
            allTeamReady = True
            self.broadcastPublisher.publish(self.robotName, currentTeam, 'READY')
            rospy.sleep(1)
            for robot in currentTeam:
                if not robot in self.readyTeam:
                    allTeamReady = False
                    break
        self.broadcastPublisher.publish(self.robotName, currentTeam, 'READY')
        print 'All team is ready'

    ##############################################
    # Terminates behaviors not in current branch #
    ##############################################
    def terminateBehaviorsNotInStack(self):
        print 'Terminating behaviors not in current branch'
        for (node, team, params) in self.nodesToTerminate:
            if not (node, team, params) in self.runningBehaviorsStack:
                print str.format('Terminating behavior: {0}', node.behaviorName)
                self.terminateBehavior(node, team)

    ############################################################
    # Terminates a behavior and informing the rest of the team #
    ############################################################
    def terminateBehavior(self, node, team):
        # Inform the rest of the robots 
        self.broadcastPublisher.publish(self.robotName, team, str.format('TERMINATING {0}', node.behaviorName))
        # Terminate the behavior
        self.terminateBehaviorPublisher.publish(node.behaviorName)
        self.behaviorsRunning.remove(node)

    #####################
    # Starts a behavior #
    #####################
    def startBehavior(self, node, params):
        # Node name with the robot name appended for namespace reasons
        fullNodeName = str.format('bite_{0}_{1}', self.robotName.lower(), node.behaviorName.lower())
        # args var is for command line input, and by default is given the robot name, each argument is
        # is seperetd by space char
        args = str.format('{0} {1} {2}', self.robotName, node.behaviorName, params)
        # Creates a node, name argument is adding robotName and _ for namespace reasons
        runNode = Node(package = self.packageName, node_type = "BehaviorLauncher.py", name = fullNodeName, args = args, output = "screen")
        # Launch node
        self.roslauncher.launch(runNode)
        self.behaviorsRunning.append(node)

    ###################################################
    # Receives information from the broadcast channel #
    ###################################################
    def receiveCallback(self, msg):
        if self.robotName in msg.to:
            if msg.data == 'READY' and not msg.from_ in self.readyTeam:
                print str.format('Received that {0} is ready', msg.from_)
                self.readyTeam.append(msg.from_)

    ###########################################
    # Monitors running behaviors in the stack #
    ###########################################

    #For each behavior in the running stack, checks if Termination- conditions apply.
    #If so: inform all robots in the team, remove behavior from execution stack
    def monitorBehaviors(self):
        behaviorsEnded = []
        # Monitors behaviors in running stack
        while behaviorsEnded == []:
            rospy.sleep(1)
            # Test all nodes in the running stack for their termination conditions
            for (node, team, params) in self.runningBehaviorsStack:
                for termCond in node.termConds:
                    # ******************************************************Should add ACTIVE PERCEPTION for Termination-conditions here*****
                    if self.getKnowledgeClient(termCond).value == 'True':
                        print str.format('I think that node {0} has to be terminated', node.nodeName)
                        behaviorsEnded.append(node)
                        # Informs the rest of the team
                        print str.format('Informing: {0}', team)
                        self.broadcastPublisher.publish(self.robotName, team, str.format('INFORM {0} {1}', termCond, True))
                        break

        # Adds nodes pending for termination
        while not behaviorsEnded == []:
            (node, team, params) = self.runningBehaviorsStack.pop()
            self.nodesToTerminate.append((node, team, params))
            if node in behaviorsEnded:
                behaviorsEnded.remove(node)

        # Returns the last node terminated
        return (node, team)

    #######################################################
    # Expands the stack sequentially                      #
    # Returns whether the stack was expanded sequentially #
    #######################################################
    def expandStackSequentially(self, currentNode, currentTeam):
        if currentNode.sequentialChildren == []:
            return False

        # Get all sequential children of current node and filter them by preconditions
        print str.format('Sequential children of node "{0}" are: {1}', currentNode.nodeName, [node.nodeName for node in currentNode.sequentialChildren])
        filteredChildren = self.filterByPreConds(currentNode.sequentialChildren)
        print str.format('Next behaviors that their preconditions are true: {0}', [node.nodeName for node in filteredChildren])

        # Set the right vote method for the last node went out of the stack
        print str.format('Node\'s vote method is: "{0}"', currentNode.voteMethod)
        voteServiceName = str.format('/bite/{0}/{1}', self.robotName, currentNode.voteMethod)
        rospy.wait_for_service(voteServiceName)
        voteClient = rospy.ServiceProxy(voteServiceName, Vote)

        if len(currentTeam) > 1:
            # Inform the rest of the team that preconditions of these behaviors are true
            print str.format('Informing the rest of the team: {0}', currentTeam)
            for node in filteredChildren:
                for preCond in node.preConds:
                    self.broadcastPublisher.publish(self.robotName, currentTeam, str.format('INFORM {0} {1}', preCond, True))

            # Sync with team
            print str.format('Waiting for team: {0}', currentTeam)
            self.waitForTeam(currentTeam)

            # Checks again after received information from other robots
            filteredChildren = self.filterByPreConds(currentNode.sequentialChildren)

            if filteredChildren == []:
                # None of the nodes fit their preconditions
                return False

            # Sleeps to make sure all the team gets here
            rospy.sleep(1)

        # Calls Vote
        result = voteClient([child.nodeName for child in filteredChildren], currentTeam)

        # Adds the node to the stack
        nextNode = self.plan.getNode(result.node)
        print str.format('Adding node "{0}" to the stack', nextNode.nodeName)
        self.runningBehaviorsStack.append((nextNode, currentTeam, result.params))
        return True

if __name__ == "__main__":
    if len(argv) < 4:
        raise Exception('Correct usage is "rosrun bite BITE.py <package_name> <robot_name> <team_member1>,...,<team_membern>')

    packageName = argv[1]
    robotName = argv[2]
    team = argv[3].split(',')

    print 'Initiating the main BITE node'
    rospy.init_node(str.format('bite_{0}_main_node', robotName.lower()))

    # Gets the plan
    packagePath = RosPack().get_path(packageName)
    plan = PlanParser(str.format('{0}/plan.xml', packagePath)).getPlan()
    bite = BITE(robotName, plan, team, packageName)

    while not rospy.is_shutdown():
        bite.expandStackHierarchically()
        rospy.sleep(1)
        # Keeps monitoring behaviors until stack is expanded sequentially
        stackExpanded = False
        while not stackExpanded:
            node, team = bite.monitorBehaviors()
            stackExpanded = bite.expandStackSequentially(node, team)
            if bite.runningBehaviorsStack == []:
                # Stack is empty. Halt.
                bite.terminateBehaviorsNotInStack()
                rospy.sleep(1)
                exit(0)

