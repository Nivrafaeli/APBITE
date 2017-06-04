#!/usr/bin/env python

import rospy
from sys import argv
from bite.srv import *

class AllocateService:
    def __init__(self, robotName):
        self.robotName = robotName

        # Providing the allocate service
        rospy.Service(str.format('/bite/{0}/allocate', self.robotName), Allocate, self.allocate)

        print 'Waiting for knowledgebase...'
        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)
        print 'Ready'

    # The allocate all method
    def allocate(self, req):
        print str.format('Allocating nodes: {0} to team: {1}', req.nodes, req.currentTeam)
        if req.nodes == []:
            return AllocateResponse('', [], '')

        node = req.nodes[0]
        params = ''

        return AllocateResponse(node, req.currentTeam, params)

if __name__ == "__main__":
    if len(argv) < 2:
        raise Exception('No robot name given')

    robotName = argv[1]

    print 'Initiating the Allocate node'
    rospy.init_node(str.format('bite_{0}_allocate_node', robotName.lower()))
    AllocateService(robotName)
    rospy.spin()
