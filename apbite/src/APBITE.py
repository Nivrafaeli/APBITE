#!/usr/bin/env python

import rospy
from rospkg import RosPack
from sys import argv
from Plan import Plan
from apbite.srv import *
from apbite.msg import *
from std_msgs.msg import String
from PlanParser import PlanParser
from roslaunch.scriptapi import ROSLaunch, Node
import std_msgs.msg


class Output:
    def __init__(self, filename):
        self.filename = filename
        HEADER="node\t action\n"
        with open(filename, 'w') as fd:
            fd.write(HEADER)

    def output_to_file(self, line):
        with open(self.filename, 'a') as fd:
            fd.write(line + "\n")

class APBITE:
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
        self.knowledgeUpdatePublisher = rospy.Publisher(str.format('/bite/{0}/knowledge_update', robotName), KnowledgeMsg,
                                                        queue_size=100)
        # Initiate subscribers
        # broadcast is the topic used for broadcast messages
        rospy.Subscriber('/bite/broadcast', InformMsg, self.receiveCallback)

        # Initiate Active perception stack

        self.Active_perception_stack = []

        print 'Waiting for knowledgebase...'
        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)

        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        LastUpdateServiceName = str.format('/bite/{0}/get_LastUpdateTime', self.robotName)
        rospy.wait_for_service(LastUpdateServiceName)
        self.getLastUpdateServiceName = rospy.ServiceProxy(LastUpdateServiceName, GetLastUpdateTimeStr)

        LastChangeServiceName = str.format('/bite/{0}/get_LastChangeTime', self.robotName)
        rospy.wait_for_service(LastChangeServiceName)
        self.getLastChangeServiceName = rospy.ServiceProxy(LastChangeServiceName, GetLastChangeTime)

        # ***********************************
        #  Active Perception block ends     #
        # ***********************************
        print 'Ready'

        rospy.sleep(0.5)
        self.logger = Output("/home/lizi-lab/Dropbox/BITE_DROPBOX/bite_drive_between_targets/logger.txt")
        self.timer = rospy.Time().now()

    def Broadcast(self, robotName, team,  data):
        h = std_msgs.msg.Header()
        h.stamp = rospy.Time.now()
        self.broadcastPublisher.publish(h, robotName, team, data)

    def update(self, key, value):
        h = std_msgs.msg.Header()
        h.stamp = rospy.Time.now()
        self.knowledgeUpdatePublisher.publish(h,str.format('{0} {1}', key, value))

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

        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        #Make sure that the single AP behaviour will be always at the buttom of the stack
        ThereIsAP=True
        TempAPstack=[]
        while ThereIsAP ==True and len(self.runningBehaviorsStack)>0:
            AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params =self.runningBehaviorsStack.pop()
            if AP_in_the_stack_Node not in plan.APplans:
                self.runningBehaviorsStack.append((AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params))
                ThereIsAP = False
            else:
                # Its an AP behavior
                ThereIsAP=True
                TempAPstack.append((AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params))
        # ***********************************
        #  Active Perception block ends     #
        # ***********************************

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

        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        #Push AP to the bottom of the stack
        while not TempAPstack  ==[]:
            self.runningBehaviorsStack.append(TempAPstack.pop())
        # ***********************************
        #  Active Perception block ends     #
        # ***********************************
        self.terminateBehaviorsNotInStack()
        rospy.sleep(1)
        print 'Starting behaviors in stack'
        for (node, team, params) in self.runningBehaviorsStack:
            if not node in self.behaviorsRunning:
                print str.format('Starting behavior: {0}', node.behaviorName)
                self.startBehavior(node, params)
                self.logger.output_to_file(str(node.nodeName) + "\tStart")
                # Notify other robots what behavior its starting
                self.Broadcast(self.robotName, self.team,  str.format('STRATING {0}', node.behaviorName))
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
                    h = std_msgs.msg.Header()
                    h.stamp = rospy.Time.now()
                    self.Broadcast(self.robotName, currentTeam, str.format('INFORM {0} {1}', preCond, True))

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
            h = std_msgs.msg.Header()
            h.stamp = rospy.Time.now()
            self.Broadcast(self.robotName, currentTeam, 'READY')
            rospy.sleep(1)
            for robot in currentTeam:
                if not robot in self.readyTeam:
                    allTeamReady = False
                    break
        h = std_msgs.msg.Header()
        h.stamp = rospy.Time.now()
        self.Broadcast(self.robotName, currentTeam, 'READY')
        print 'All team is ready'

    ##############################################
    # Terminates behaviors not in current branch #
    ##############################################
    def terminateBehaviorsNotInStack(self):
        #print 'Terminating behaviors not in current branch'
        for (node, team, params) in self.nodesToTerminate:
            if not (node, team, params) in self.runningBehaviorsStack:
                #print str.format('Terminating behavior: {0}', node.behaviorName)
                self.terminateBehavior(node, team)
                self.logger.output_to_file(str(node.nodeName) + "\tTerminate")

    ############################################################
    # Terminates a behavior and informing the rest of the team #
    ############################################################
    def terminateBehavior(self, node, team):
        # Inform the rest of the robots
        h = std_msgs.msg.Header()
        h.stamp = rospy.Time.now()
        self.Broadcast(self.robotName, team, str.format('TERMINATING {0}', node.behaviorName))
        # Terminate the behavior
        self.terminateBehaviorPublisher.publish(node.behaviorName)
        self.behaviorsRunning.remove(node)
        if node in self.Active_perception_stack:
            self.Active_perception_stack.remove(node)
            rospy.logerr("*** Terminating " + str(node.behaviorName) + " from AP stack ")


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

    # ***********************************
    #  Active Perception block starts   #
    # ***********************************

    def updateMissingBeliefs(self):
        if SECS_TO_MISS_OBSTACELONTHEWAY<0 or SECS_TO_MISS_KNOWSTARGETLOCATION<0:
            rospy.logerr("*** Can not perform Active Perception because the SECS_TO_MISS are negative ")
        else:
            #Beliefs Status Monitor gets list B of beliefs and:
            #1-For each belief b in B gets:
                #1- Name
                #2- Rules to be "Known"
                #3- Rules to be "OutDated"


            #2 - For each belief
                #1- If b is not in knowledge or b was never updated:
                        #If (b_STATUS is not unknown or b_STATUS is not updating):
                            #b_STATUS = Unknown
                        #else:
                            #do nothing
                    #Else:
                        #If (The rull of being known apply):
                            #b_STATUS = known
                        #Else:
                            #If (rull to be outdated apply):
                                #b_STATUS = outdated
                            #else:
                                #b_STATUS = Assumed
            '''
            #IMPLEMENTATION OF 2:
            # 2 - For each belief
            for bel in BELIEFSMONITOR_LIST:
                b_name =bel.Name
                b_knownrules=bel.knownRules
                b_outdatedrules=bel.OutdatedRules
                # 1- If b  was never updated:   (or is not in knowledge or b)
                b_LastUpdate=self.getLastUpdateTime(b_name).LastUpdateTime
                if b_LastUpdate=='False':
                    b_STATUS_value=self.getKnowledgeClient(bel.Name+"_STATUS").value
                    #(This belief is unknown)
                    if  b_STATUS_value is not "Unknown" and b_STATUS_value is not "Updating":
                        # b_STATUS = Unknown
                        self.update(bel.Name+"_STATUS", 'Unknown')
                        self.update(bel.Name, 'Missing')
                else:
                    knownApply=True
                    for rule in b_knownrules:
                        if self.getKnowledgeClient(rule).value is not b_knownrules[rule]:
                            knownApply=False
                    # If (The rull of being known apply):
                    if knownApply==True:
                        # b_STATUS = known
                        self.update(bel.Name + "_STATUS", 'Known')
                    # Else:
                    else:
                        OutdatedApply=True
                        for rule in b_outdatedrules:
                            now = rospy.Time.now()
                            t = SECS_TO_MISS_OBSTACELONTHEWAY
                            t_secs_ago = now - rospy.Duration(t)  # Time minus Duration is a Time
                            t_secs_ago = int(str(t_secs_ago))
                            last_updated_time = self.getLastChangedTime('ObstacleOnTheWay_time').value

                        # If (rull to be outdated apply):
                        if
                            # b_STATUS = Missing
                        # else:
                            # b_STATUS = Assumed

            '''

            # This function purpose is to update missing beliefs as 'Missing'
            now = rospy.Time.now()

            #1- I dont want to active more than t seconds without looking down
            t=SECS_TO_MISS_OBSTACELONTHEWAY
            t_secs_ago = now - rospy.Duration(t)  # Time minus Duration is a Time
            last_updated_time_sec = self.getLastUpdateServiceName('ObstacleOnTheWay').sec
            bel_value=self.getKnowledgeClient('ObstacleOnTheWay').value
            #DEBBUGGING
            if last_updated_time_sec=='False':
                rospy.loginfo("{0}: ObstacleOnTheWay is UNKNOWN".format("APBITE"))
            else:
                now_float=now.to_sec()
                rospy.loginfo("{0}: ObstacleOnTheWay was updated {1} seconds ago".format("APBITE",now_float-float(self.getLastUpdateServiceName('ObstacleOnTheWay').sec)))
            # DEBBUGGING END

            if self.getKnowledgeClient('Driving').value=='True': #If the agent is driving
                if last_updated_time_sec=='False':#If it is unknown (never been updated)
                    self.update('ObstacleOnTheWay', 'Missing')
                    rospy.loginfo("{0}: ObstacleOnTheWay is UNKNOWN - look down".format("APBITE"))
                else: #If it is known but last updated time is longer than t
                    last_updated_time = rospy.Time.from_sec(float(last_updated_time_sec))
                    if last_updated_time < t_secs_ago and bel_value is not "Missing":
                        self.update('ObstacleOnTheWay', 'Missing')
                        #**self.update('ObstacleOnTheWay_time', now)
                        rospy.loginfo("{0}: ObstacleOnTheWay is OUTDATED - look down".format("APBITE"))

            #2- I dont want to colide on the target, so if i didn't see it for more then 1 second i want to look up at it
            t = SECS_TO_MISS_KNOWSTARGETLOCATION
            t_secs_ago = now - rospy.Duration(t)  #Time minus Duration is a Time
            last_updated_time_sec = self.getLastUpdateServiceName('KnowsTargetLocation').sec
            bel_value = self.getKnowledgeClient('KnowsTargetLocation').value
            #If it was never known
            # DEBBUGGING
            if last_updated_time_sec == 'False':
                rospy.loginfo("{0}: KnowsTargetLocation is UNKNOWN".format("APBITE"))
            else:
                now_float = now.to_sec()
                rospy.loginfo("{0}: KnowsTargetLocation was updated {1} seconds ago".format("APBITE",now_float-float(self.getLastUpdateServiceName('KnowsTargetLocation').sec)))
                # DEBBUGGING END
            if self.getKnowledgeClient('Driving').value == 'True' or self.getKnowledgeClient('SearchingTarget').value == 'True':
                if last_updated_time_sec == 'False':
                    self.update('KnowsTargetLocation', 'Missing')
                    rospy.loginfo("{0}: TargetLocation is UNKNOWN - look up".format("APBITE"))
                else:
                    # If it is known but updated long time ago
                    last_updated_time = rospy.Time.from_sec(float(last_updated_time_sec))
                    if last_updated_time<t_secs_ago and bel_value is not "Missing":
                        self.update('KnowsTargetLocation', 'Missing')
                        rospy.loginfo("{0}: TargetLocation is OUTDATED - look up".format("APBITE"))

        # ***********************************
        #  Active Perception block ends     #
        # ***********************************

        #For each behavior in the running stack, checks if Termination- conditions apply.
        #If so: inform all robots in the team, remove behavior from execution stack
    def monitorBehaviors(self):
        behaviorsEnded = []
        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        TermCondMissing = [] #Missing Termination conditions
        SupportBelMissing = [] #Missing Supporting beliefs

        # ***********************************
        #  Active Perception block ends     #
        # ***********************************
        # Monitors behaviors in running stack
        while (behaviorsEnded == [] and TermCondMissing==[] and SupportBelMissing==[]) and not rospy.is_shutdown() :
            rospy.sleep(1)
            # Test all nodes in the running stack for their termination conditions
            # ***********************************
            #  Active Perception block starts   #
            # ***********************************

            if rospy.Time().now() - self.timer > rospy.Duration(0.5):
                self.timer = rospy.Time().now()
                #self.reviseBeliefs()
                self.updateMissingBeliefs()

            # ***********************************
            #  Active Perception block ends     #
            # ***********************************

            for (node, team, params) in self.runningBehaviorsStack:
                for termCond in node.termConds:
                    if self.getKnowledgeClient(termCond).value == 'True':
                        print str.format('I think that node {0} has to be terminated', node.nodeName)
                        behaviorsEnded.append(node)
                        # Informs the rest of the team
                        print str.format('Informing: {0}', team)
                        h = std_msgs.msg.Header()
                        h.stamp = rospy.Time.now()
                        self.Broadcast(self.robotName, team, str.format('INFORM {0} {1}', termCond, True))
                        break
                    # ***********************************
                    #  Active Perception block starts   #
                    # ***********************************
                    if self.getKnowledgeClient(termCond).value == 'Missing':#beliefs can be either {True, False, Missing, Updating}
                        #print str.format('Belief {0} in node {1} is missing', termCond, node.nodeName)
                        Missing_term_belief=termCond
                        TermCondMissing.append((node,Missing_term_belief))
                        #break
                for supportBel in node.supportBels:
                    if self.getKnowledgeClient(supportBel).value == 'Missing':  # beliefs can be either {True, False, Missing, Updating}
                        #print str.format('Belief {0} in node {1} is missing', supportBel, node.nodeName)
                        Missing_support_belief = supportBel
                        SupportBelMissing.append((node,Missing_support_belief))
                        #break
                    # ***********************************
                    #  Active Perception block ends     #
                    # ***********************************
        # Adds nodes pending for termination
        TE=[]
        MT=[]
        MS=[]
        #print "1"
        node=team=None
        while not behaviorsEnded == []:
           # print "a"
            (node, team, params) = self.runningBehaviorsStack.pop()
            self.nodesToTerminate.append((node, team, params))
            if node in behaviorsEnded:
                behaviorsEnded.remove(node)
        if node is not None:
            TE.append((node, team))
        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        while TE==[] and not TermCondMissing == []:
            #print "b"
            for Missing_node,mtb in TermCondMissing:
                for (node, team, params) in self.runningBehaviorsStack:
                    if node == Missing_node:
                        #MT contains the missing behavior, the team that runs it, and the missing termination belief
                        MT.append(((node, team, params),mtb))
                        TermCondMissing.remove((Missing_node,mtb))

        while TE==[] and not SupportBelMissing == []:
            #print "c"
            for Missing_node, msb in SupportBelMissing:
                print "Missing: " + str(Missing_node.nodeName)
                for (node, team, params) in self.runningBehaviorsStack:
                    print "Checking: " + str(node.nodeName)
                    if node == Missing_node:
                        # MS contains the missing behavior, the team that runs it, and the missing termination belief
                        MS.append(((node, team, params),msb))
                        SupportBelMissing.remove((Missing_node, msb))
        # ***********************************
        #  Active Perception block ends     #
        # ***********************************
        # Returns the last node terminated or the node,team,termcond of the missing belief
        #print "2"
        print "Monitor phase summary"
        print "TE"
        for (node, team) in TE:
            print "Node" + node.nodeName + " Terminated"
        print "MT"
        for ((node, team, params), msb) in MT:
            print "In node " + node.nodeName + " Missing Termination belief: " + str(msb)
        print "MS"
        for ((node, team, params), msb) in MS:
            print "In node "+ node.nodeName + " Missing Support belief: "+str(msb)
        return (TE,MT,MS)
        print "End of Monitor phase summary"

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
            #print str.format('Informing the rest of the team: {0}', currentTeam)
            for node in filteredChildren:
                for preCond in node.preConds:
                    h = std_msgs.msg.Header()
                    h.stamp = rospy.Time.now()
                    self.Broadcast(self.robotName, currentTeam, str.format('INFORM {0} {1}', preCond, True))

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
        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        # Make sure that the single AP behaviour will be always at the buttom of the stack
        ThereIsAP = True
        TempAPstack = []
        while ThereIsAP == True and len(self.runningBehaviorsStack)>0:
            AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params = self.runningBehaviorsStack.pop()
            if AP_in_the_stack_Node not in plan.APplans:
                self.runningBehaviorsStack.append((AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params))
                ThereIsAP = False
            else:
                # Its an AP behavior
                ThereIsAP = True
                TempAPstack.append((AP_in_the_stack_Node, AP_in_the_stack_Team, AP_in_the_stack_params))



        # ***********************************
        #  Active Perception block ends     #
        # ***********************************

        self.runningBehaviorsStack.append((nextNode, currentTeam, result.params))
        # ***********************************
        #  Active Perception block starts   #
        # ***********************************
        while not TempAPstack == []:
            self.runningBehaviorsStack.append(TempAPstack.pop())
        # ***********************************
        #  Active Perception block ends     #
        # ***********************************
        return True

    def getApPlan(self,missing_belief):
        return self.plan.getAPplan(missing_belief)


SECS_TO_MISS_OBSTACELONTHEWAY=0.4
SECS_TO_MISS_KNOWSTARGETLOCATION=0.4
BELIEFSMONITOR_LIST=[]

# ***********************************
#  Active Perception block starts   #
# ***********************************
class BeliefRulesForMonitor:
    def __init__(self, belName, knownRules, OutdatedRules):
        self.Name = belName
        self.knownRules = knownRules
        self.OutdatedRules = OutdatedRules

# ***********************************
#  Active Perception block ends   #
# ***********************************

if __name__ == "__main__":
    #In order to control the missing beliefs parameters I had to add another 2 additional parameters
    #if len(argv) < 5:
    if len(argv) < 7:
        raise Exception('Correct usage is "rosrun bite APBITE.py <package_name> <robot_name> <team_member1>,...,<team_membern>')

    packageName = argv[1]
    robotName = argv[2]
    team = argv[3].split(',')
    method = argv[4]
    secs_to_miss_ObstacleOnTheWay_str = argv[5]
    secs_to_miss_KnowsTargetLocation_str = argv[6]
    print "Method "+method

    if method=="false" or method==None:
        exit(0)
    if secs_to_miss_ObstacleOnTheWay_str=="false" or secs_to_miss_ObstacleOnTheWay_str==None:
        exit(0)
    if secs_to_miss_KnowsTargetLocation_str=="false" or secs_to_miss_KnowsTargetLocation_str==None:
        exit(0)

    SECS_TO_MISS_OBSTACELONTHEWAY = float(secs_to_miss_ObstacleOnTheWay_str)
    SECS_TO_MISS_KNOWSTARGETLOCATION = float(secs_to_miss_KnowsTargetLocation_str)


    print 'Initiating the main BITE node'
    print 'SECS_TO_MISS_OBSTACELONTHEWAY' + str(SECS_TO_MISS_OBSTACELONTHEWAY)
    print 'SECS_TO_MISS_KNOWSTARGETLOCATION' + str(SECS_TO_MISS_KNOWSTARGETLOCATION)

    #In this implementation the rules of changing from Kno
    BELIEFSMONITOR_LIST.append(BeliefRulesForMonitor("ObstacleOnTheWay",{"CameraDown":"True"}, {"ObstacleOnTheWay":SECS_TO_MISS_OBSTACELONTHEWAY}))
    BELIEFSMONITOR_LIST.append(BeliefRulesForMonitor("KnowsTargetLocation",{"CameraUp":"True"} ,{"KnowsTargetLocation":SECS_TO_MISS_KNOWSTARGETLOCATION}))



    rospy.init_node(str.format('bite_{0}_main_node', robotName.lower()))

    # Gets the plan
    packagePath = RosPack().get_path(packageName)
    if method=="apbite":
        plan = PlanParser(str.format('{0}/plan.xml', packagePath)).getPlan()
    elif method=="opt":
        plan = PlanParser(str.format('{0}/plan_opt.xml', packagePath)).getPlan()
    elif method == "lookdown":
        plan = PlanParser(str.format('{0}/plan_lookdown.xml', packagePath)).getPlan()
    elif method=="lookup":
        plan = PlanParser(str.format('{0}/plan_lookup.xml', packagePath)).getPlan()
    else:
        exit(0)

    print "**Printing:**"
    plan.printPlan()
    bite = APBITE(robotName, plan, team, packageName)
    # ***********************************
    #  Active Perception block starts   #
    # ***********************************
    bite.Active_perception_stack=[]
    #in this iteration im using it only to make sure that there is only one ap activity in stack
    # ***********************************
    #  Active Perception block ends     #
    # ***********************************
    while not rospy.is_shutdown():
        print "Running behaviors List:"
        for node in bite.behaviorsRunning:
            print node.nodeName
        print "End of Running behaviors List"
        bite.expandStackHierarchically()
        rospy.sleep(1)
        # Keeps monitoring behaviors until stack is expanded sequentially
        stackExpanded = False
        while not stackExpanded and not rospy.is_shutdown():
            print "Running behaviors List:"
            for node in bite.behaviorsRunning:
                print node.nodeName
            print "End of Running behaviors List"
            '''
            #before APbite
            (node, team) = bite.monitorBehaviors()
            '''
            TE, MT, MS = bite.monitorBehaviors()
            if not TE==[]:
                (node, team)=TE[0]
                stackExpanded = bite.expandStackSequentially(node, team)
                bite.terminateBehaviorsNotInStack()
                bite.nodesToTerminate=[]
            # ***********************************
            #  Active Perception block starts   #
            # ***********************************
            else:#MT or MS is not None
                #Implement Handle missing during execution
                AP=[]
                # 1. get AP for mb
                AP.extend([(a, bite.getApPlan(mb),mb) for a, mb in MT ])
                AP.extend([(a, bite.getApPlan(mb),mb) for a, mb in MS])


                AP_StatusStr1="AP_mb_list:"
                for a, ap, missingb in AP:
                    AP_StatusStr1 = AP_StatusStr1 + " |" + missingb
                AP_StatusStr1 = AP_StatusStr1 + " "

                # 2. choose a single AP plan to add to the stack
                    #In this implementation we choose randomly
                import random
                selected_AP=random.choice(AP)
                missingNodeData, ActivePerceptionPlan, mb=selected_AP


                AP_StatusStr2 = ",Chosen_mb_toSolve:"+str(mb)
                AP_StatusStr3 = ",Status:"


                # 3. push a single AP plan to stack, only if it is missing
                if len(bite.Active_perception_stack)<1:
                    AP_StatusStr3 = AP_StatusStr3+"STARTS"
                    missing_node,missing_team,params =missingNodeData
                    rospy.logerr("*** Pushing " + str(ActivePerceptionPlan.behaviorName) + " into AP stack ")
                    bite.Active_perception_stack.append(ActivePerceptionPlan)
                    #The whole team will execute the AP process
                    #push into stack
                    bite.runningBehaviorsStack.append((ActivePerceptionPlan, missing_team, ''))
                    #Change the status of the Missing belief to 'Updated'
                    #So APBITE will not push other relevant ap-plans for the same missing belief
                    bite.update(mb, 'Updating')
                    #**bite.update(mb+"_time", rospy.Time.now())
                    #expend
                    bite.expandStackHierarchically()
                else:
                    AP_StatusStr3 = AP_StatusStr3 + "BLOCKED"
                    rospy.logerr ("*** Can not push " +str(ActivePerceptionPlan.behaviorName) + " into AP stack, there is another active AP process ")
                bite.update("AP_STATUS", AP_StatusStr1+AP_StatusStr2+AP_StatusStr3)
            # ***********************************
            #  Active Perception block ends     #
            # ***********************************

            if bite.runningBehaviorsStack == []:
                # Stack is empty. Halt.
                bite.terminateBehaviorsNotInStack()
                rospy.sleep(1)
                exit(0)


