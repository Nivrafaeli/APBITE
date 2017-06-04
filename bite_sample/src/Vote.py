#!/usr/bin/env python

import rospy
from sys import argv
from bite.srv import *

class VoteService:
    def __init__(self, robotName):
        self.robotName = robotName

        # Providing the allocate service
        rospy.Service(str.format('/bite/{0}/vote', self.robotName), Vote, self.vote)

        print 'Waiting for knowledgebase...'
        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)
        print 'Ready'

    # The vote method
    def vote(self, req):
        print str.format('Voting for nodes: {0} to team: {1}', req.nodes, req.currentTeam)
        if req.nodes == []:
            return VoteResponse('', '')

        node = req.nodes[0]
        params = ''

        return VoteResponse(node, params)

if __name__ == "__main__":
    if len(argv) < 2:
        raise Exception('No robot name given')

    robotName = argv[1]

    print 'Initiating the Vote node'
    rospy.init_node(str.format('bite_{0}_vote_node', robotName.lower()))
    VoteService(robotName)
    rospy.spin()
