import rospy, threading, tf

MARKER_LIST = ["4x4_73", "4x4_59"]

class MarkerThread(threading.Thread):
    WAITING_DURATION = 1.0

    def __init__(self, marker_name, robot_name, ):
        self.marker_name = marker_name
        self.robot_name = robot_name
        self.should_run = True
        self.listener = tf.TransformListener()

    def getTransform(self, target_frame, dest_frame):
        try:
            self.listener.waitForTransform(target_frame, dest_frame, rospy.Time.now(), rospy.Duration(self.WAITING_DURATION))
            trans, rot = self.listener.lookupTransform(target_frame, dest_frame, rospy.Time(0))
        except (tf.Exception,tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            trans, rot = (None, None)
        return trans, rot

    def run(self):
        while self.should_run:
            pass

    def stop(self):
        self.should_run = False
