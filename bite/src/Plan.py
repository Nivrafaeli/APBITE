class Plan:
    # Represents a node in the plan
    class Node:
        def __init__(self, nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod):
            self.nodeName = nodeName
            self.behaviorName = behaviorName
            self.preConds = preConds
            self.termConds = termConds
            self.allocateMethod = allocateMethod
            self.voteMethod = voteMethod
            self.hierarchicalChildren = []
            self.sequentialChildren = []

    # Initiate an empty list of nodes
    def __init__(self):
        self.nodes = []

    # Adds a node to the plan
    def addNode(self, nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod):
        if nodeName in [node.nodeName for node in self.nodes]:
            print nodeName
            raise Exception('Node name must be unique' )
        self.nodes.append(self.Node(nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod))

    # Gets a node by name
    def getNode(self, nodeName):
        index = [node.nodeName for node in self.nodes].index(nodeName)
        return self.nodes[index]

    # Adds an hierarchical edge
    def addHierarchicalEdge(self, parentNodeName, childNodeName):
        # Checks if the nodes we are connecting were set beforehand
        if not parentNodeName in [node.nodeName for node in self.nodes]:   
            raise Exception(str.format('No such node {0}', parentNodeName))
        if not childNodeName in [node.nodeName for node in self.nodes]:
            raise Exception (str.format('No such node {0}', childNodeName))
        parentNode = self.getNode(parentNodeName)
        childNode = self.getNode(childNodeName)
        parentNode.hierarchicalChildren.append(childNode)
        
    # Adds a sequential edge
    def addSequentialEdge(self, parentNodeName, childNodeName):
        # Checks if the nodes we are connecting were set beforehand
        if not parentNodeName in [node.nodeName for node in self.nodes]:   
            raise Exception(str.format('No such node {0}', parentNodeName))
        if not childNodeName in [node.nodeName for node in self.nodes]:
            raise Exception (str.format('No such node {0}', childNodeName))
        parentNode = self.getNode(parentNodeName)
        childNode = self.getNode(childNodeName)
        parentNode.sequentialChildren.append(childNode)
