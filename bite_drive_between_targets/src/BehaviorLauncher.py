#!/usr/bin/env python

import rospy
from sys import argv
from std_msgs.msg import String

# Import all behaviors here ->
from Initiate import Initiate
from ChooseTarget import ChooseTarget
from SearchTarget import SearchTarget
from GoToTarget import GoToTarget

from LookForObstacle import LookForObstacle
from LookDown import LookDown
from FindTarget import FindTarget
from LookUp import LookUp

from AtTarget import AtTarget
from AtObstacle import AtObstacle
from Termination import Termination

from TurnLeft90 import TurnLeft90




class BehaviorLauncher:
    def __init__(self, robotName, behaviorName, params):
        self.behaviorName = behaviorName
        eval(behaviorName)(robotName, behaviorName, params).run()

if __name__ == '__main__':
    robotName = argv[1]
    behaviorName = argv[2]
    params = argv[3].split(',')

    rospy.init_node(str.format('bite_{0}_{1}', robotName.lower(), behaviorName.lower()))
    BehaviorLauncher(robotName, behaviorName, params)
    
    rospy.spin()
