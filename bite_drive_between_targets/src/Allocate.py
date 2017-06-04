#!/usr/bin/env python

import rospy
from sys import argv
from apbite.srv import *

class AllocateService:
    def __init__(self, robotName):
        self.robotName = robotName

        # Providing the allocate service
        rospy.Service(str.format('/bite/{0}/allocate_all', self.robotName), Allocate, self.allocateAll)
        rospy.Service(str.format('/bite/{0}/allocate_separate', self.robotName), Allocate, self.allocateSeparate)
        rospy.Service(str.format('/bite/{0}/allocate_half', self.robotName), Allocate, self.allocateHalf)

        print 'Waiting for knowledgebase...'
        knowledgeServiceName = str.format('/bite/{0}/get_knowledge', self.robotName)
        rospy.wait_for_service(knowledgeServiceName)
        self.getKnowledgeClient = rospy.ServiceProxy(knowledgeServiceName, GetKnowledge)
        print 'Ready'

    # The allocate all method
    def allocateAll(self, req):
        print str.format('Allocating nodes: {0} to team: {1}', req.nodes, req.currentTeam)
        if req.nodes == []:
            return AllocateResponse('', [], '')

        node = req.nodes[0]
        params = ''

        return AllocateResponse(node, req.currentTeam, params)

    # The allocate separate method
    def allocateSeparate(self, req):
        print str.format('Allocating nodes: {0} to team: {1}', req.nodes, req.currentTeam)
        if req.nodes == []:
            return AllocateResponse('', [], '')

        req.currentTeam.sort()
        if self.robotName == req.currentTeam[0]:
            node = req.nodes[0]
            newTeam = [self.robotName]
        else:
            node = req.nodes[1]
            newTeam = req.currentTeam[1:]
        params = ''

        return AllocateResponse(node, newTeam, params)

    def allocateHalf(self, req):
        print str.format('Allocating nodes: {0} to team: {1}', req.nodes, req.currentTeam)
        if req.nodes == []:
            return AllocateResponse('', [], '')

        req.currentTeam.sort()
        half = len(req.currentTeam) / 2
        if self.robotName in req.currentTeam[:half]:
            newTeam = req.currentTeam[:half]
            params = 'left'
        else:
            newTeam = req.currentTeam[half:]
            params = 'right'

        return AllocateResponse(req.nodes[0], newTeam, params)

if __name__ == "__main__":
    if len(argv) < 2:
        raise Exception('No robot name given')

    robotName = argv[1]

    print 'Initiating the Allocate node'
    rospy.init_node(str.format('bite_{0}_allocate_node', robotName.lower()))
    AllocateService(robotName)
    rospy.spin()
