import xml.etree.ElementTree as ET
from Plan import Plan

class PlanParser:
    # XML parser for creating a plan
    def __init__(self, fileName):
        self.fileName = fileName
        self.plan = Plan()

    def parseNode(self, nodeData):
        # Gets the node's data from the node element
        nodeName = nodeData.attrib['nodeName']
        behaviorName = nodeData.find('behaviorName').text
        preConds = [preCond.text for preCond in nodeData.findall('preCond')]
        termConds = [termCond.text for termCond in nodeData.findall('termCond')]
        allocateMethod = nodeData.find('allocateMethod').text
        voteMethod = nodeData.find('voteMethod').text

        # Adds the node into the plan
        self.plan.addNode(
	        nodeName = nodeName,\
         	behaviorName = behaviorName,\
	        preConds = preConds,\
	        termConds = termConds,\
	        allocateMethod = allocateMethod,\
	        voteMethod = voteMethod)


    def parseHierarchicalEdge(self, hierarchicalEdgeData):
        # Gets the edge's attributes
        fromNode = hierarchicalEdgeData.get('from')
        toNode = hierarchicalEdgeData.get('to')
        # Adds the edge to the plan
        self.plan.addHierarchicalEdge(fromNode, toNode)

    def parseSequentialEdge(self, sequentialEdgeData):
        # Gets the edge's attributes
        fromNode = sequentialEdgeData.get('from')
        toNode = sequentialEdgeData.get('to')
        # Adds the edge to the plan
        self.plan.addSequentialEdge(fromNode, toNode)

    def getPlan(self):
        tree = ET.parse(self.fileName)
        root = tree.getroot()

        # Adds all nodes to the plan
        nodes = root.find('nodes')
        for node in nodes:
            self.parseNode(node)

        # Adds all edges to the plan
        heirarchicalEdges = root.find('heirarchicalEdges')
        for heirarchicalEdge in heirarchicalEdges:
            self.parseHierarchicalEdge(heirarchicalEdge)
        sequentialEdges = root.find('sequentialEdges')
        for sequentialEdge in sequentialEdges:
            self.parseSequentialEdge(sequentialEdge)

        return self.plan

