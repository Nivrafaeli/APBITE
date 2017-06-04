import xml.etree.ElementTree as ET

class DependenciesParser:
    # XML parser for getting behaviors dependencies
    def __init__(self, fileName):
        self.fileName = fileName
        self.behaviorDependencies = {}

    def parseNode(self, behaviorData):
        # Gets the behavior name from the coralletd attribute
        behaviorName = behaviorData.attrib['name']
        # Iterates through all behavior's dependencies
        for dependency in behaviorData.findall('dependency'):
            if dependency.text not in self.behaviorDependencies:
                # Creates a new array of behaviors for this dependency
                self.behaviorDependencies[dependency.text] = [behaviorName]
            elif not behaviorName in self.behaviorDependencies[dependency.text]:
                # Adds the behavior to the array
                self.behaviorDependencies[dependency.text].append(behaviorName)

    def getBehaviorDependencies(self):
        tree = ET.parse(self.fileName)
        root = tree.getroot()
        # Iterates through all the behaviors
        for behavior in root.findall('behavior'):
            self.parseNode(behavior)
        return self.behaviorDependencies
