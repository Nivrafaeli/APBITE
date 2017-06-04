#!/usr/bin/env python
import rospy
from sys import argv
from geometry_msgs.msg import Transform
from std_msgs.msg import Float64

if __name__ == "__main__":
    if len(argv) < 2:
        raise Exception('No robot name given')
    rospy.init_node("TopicsNode")
    #This node keeps the topics open
    robotName = argv[1]
    publishers=[]
    for i in xrange(4):
        topic = str.format('/{0}/transformation/{1}', robotName, i)
        publisher = rospy.Publisher(topic, Transform, queue_size=30)
        publishers.append(publisher)
    cam_control = rospy.Publisher(str.format('/lizi_1/tilt_controller/command', robotName), Float64,
                                       queue_size=100)
    rospy.spin()