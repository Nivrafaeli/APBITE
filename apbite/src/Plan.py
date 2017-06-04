class Plan:
    # Represents a node in the plan
    class Node:
        def __init__(self, nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod,supportBels):
            self.nodeName = nodeName
            self.behaviorName = behaviorName
            self.preConds = preConds
            self.termConds = termConds
            self.allocateMethod = allocateMethod
            self.voteMethod = voteMethod
            self.hierarchicalChildren = []
            self.sequentialChildren = []
            self.supportBels = supportBels
    # Initiate an empty list of nodes
    def __init__(self):
        self.nodes = []
        # ***********************************
        #  Active Perception block starts   #
        # ***********************************

        self.APplans=[]

        # ***********************************
        #  Active Perception block ends     #
        # ***********************************

    # Adds a node to the plan
    def addNode(self, nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod,supportBels):
        if nodeName in [node.nodeName for node in self.nodes]:
            print nodeName
            raise Exception('Node name must be unique' )
        self.nodes.append(self.Node(nodeName, behaviorName, preConds, termConds, allocateMethod, voteMethod,supportBels))

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

    # ***********************************
    #  Active Perception block starts   #
    # ***********************************

    def addAPplan(self,forMissingBeliefe, APplanNode):
    # Checks if the nodes we are about to activate as APplan is set beforehand
        if not APplanNode in [node.nodeName for node in self.nodes]:
            raise Exception(str.format('No such node {0}', APplanNode))
        APplan = self.getNode(APplanNode)
        self.APplans.append((forMissingBeliefe,APplan))

    def getAPplan(self,forMissingBeliefe):
        for mb,applan in self.APplans:
            if mb==forMissingBeliefe:
                return applan
        raise Exception(str.format('There is no Active Perception for {0}', forMissingBeliefe))

    def printNode(self,node):
        print ""
        print node.nodeName
        print node.behaviorName
        print node.preConds
        print node.termConds
        print node.allocateMethod
        print node.voteMethod
        print node.hierarchicalChildren
        print node.sequentialChildren
        print "Support bel:"
        print node.supportBels

    def printPlan(self):
        print "Ap-Plans:"
        for APplan in self.APplans:
            print APplan
        print ""
        print "Nodes:"
        for node in self.nodes:
            self.printNode(node)
    # ***********************************
    #  Active Perception block ends     #
    # ***********************************
