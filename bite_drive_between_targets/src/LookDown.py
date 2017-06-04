import rospy
from BehaviorBase import BehaviorBase
from std_msgs.msg import Float64

class LookDown(BehaviorBase):
    def __init__(self, robotName, behaviorName, params):
        BehaviorBase.__init__(self, robotName, behaviorName, params)
        rospy.sleep(0.5)
        self.cam_control = rospy.Publisher(str.format('/lizi_1/tilt_controller/command', robotName), Float64, queue_size=10)

    def run(self):
        print "*** LookDown ***"
        msg = Float64()  # The default constructor will set all commands to 0
        msg.data = 0.8

        #while self.getKnowledge('UsingCamera')=="True" and not rospy.is_shutdown():
        #    rospy.logerr("Trying to look down - but camera is in use")
        #    rospy.sleep(0.2) #Waiting here for the camera to be free

        #self.update('UsingCamera', 'True')
        self.update('CameraUp', 'False')
        now = rospy.Time.now()
        t = 0.5
        finish_time = now + rospy.Duration(t)  # Time minus Duration is a Time
        print "************look down ******************"
        while not rospy.is_shutdown() and now<finish_time:
            self.cam_control.publish(msg)
            now = rospy.Time.now()
        print "************look down finished ******************"
        self.update('CameraDown', 'True')
        #self.update('UsingCamera', 'False')

