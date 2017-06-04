import rospy
import math
import tf
from threading import Thread, Lock
from geometry_msgs.msg import Transform
import copy

class MarkerThread(Thread):
    WAITING_DURATION = 1.0

    def __init__(self,thread_name,target_name, dest_name):
        Thread.__init__(self)
        self.thread_name=thread_name
        self.target_name = target_name
        self.dest_name = dest_name
        self.should_run = True
        self.trans = None
        self.rot = None
        self.listener = tf.TransformListener()
        rospy.sleep(0.5) # Otherwise first waitForTransform will throw an exception.
        self.mutex= Lock()

    def run(self):
        while self.should_run and not rospy.is_shutdown():
            rospy.sleep(0.1)
            try:
                self.listener.waitForTransform(self.target_name, self.dest_name, rospy.Time.now(),rospy.Duration(self.WAITING_DURATION))
                self.trans, self.rot = self.listener.lookupTransform(self.target_name, self.dest_name, rospy.Time(0))
            except (tf.Exception, tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                self.trans, self.rot = (None, None)


    def stop(self):
        self.should_run = False

    def copyTransRot(self,trans,rot):
        transform = Transform()
        transform.translation.x=trans[0]
        transform.translation.y = trans[1]
        transform.translation.z = trans[2]
        transform.rotation.x=rot[0]
        transform.rotation.y=rot[1]
        transform.rotation.z=rot[2]
        transform.rotation.w=rot[3]
        return transform

    def publishTransRot(self,publisher):
        trans = copy.deepcopy(self.trans)
        rot = copy.deepcopy(self.rot)
        if trans is not None and rot is not None:
            transform=self.copyTransRot(trans,rot)
            try:
                publisher.publish(transform)
            except:
                u=1
            return True
        return False

    def getTransRot(self):
        trans = copy.deepcopy(self.trans)
        rot = copy.deepcopy(self.rot)
        return trans,rot

class ReportAgentsLocation(Thread):
    def __init__(self, robotName, report_topic_mylocation):
        Thread.__init__(self)
        self.publisher = rospy.Publisher(report_topic_mylocation, Transform, queue_size=30)
        #self.my_thread = MarkerThread("Thread"+"Mylocation", robotName+"/odom_link", robotName)
        self.my_thread = MarkerThread("Thread_Mylocation", "map", robotName+"/dummy_link")
        self.my_thread.start()
        self.should_run = True
        try:
            self.publisher.publish(Transform())
        except :
            u=1
            print "Cant publish"

    def __del__(self):
        self.my_thread.stop()
        self.my_thread.join()
        self.publisher.unregister()

    def run(self):
        rate = rospy.Rate(20)
        while ((self.should_run) and (not rospy.is_shutdown())):
            found = False
            trans, rot = self.my_thread.getTransRot()
            found = trans is not None and rot is not None
            if found:
                try:
                    self.publisher.publish(self.my_thread.copyTransRot(trans, rot))
                except:
                    u=1
                break
            if not found:
                try:
                    self.publisher.publish(Transform())
                except:
                    u = 1
                    print "Cant publish2"
            rate.sleep()

    def stop(self):
        self.should_run = False

class ReportLocation(Thread):
    def __init__(self, robotName, targetNum, topic_name,markerNames):
        Thread.__init__(self)
        self.robotName = robotName
        self.targetNum = targetNum
        self.topic_name = topic_name
        self.threads = []
        self.publisher = rospy.Publisher(topic_name, Transform, queue_size=30)
        for marker_name in markerNames:
            my_frame= robotName + "/base_link"
            dest_frame=marker_name
            my_thread = MarkerThread("Thread"+str(dest_frame), my_frame, dest_frame)
            my_thread.start()
            self.threads.append(my_thread)
        self.should_run = True
        try:
            self.publisher.publish(Transform())
        except :
            u=1

    def __del__(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        self.publisher.unregister()

    def run(self):
        while ((self.should_run) and (not rospy.is_shutdown())):
            found = False
            for marker in self.threads:
                #found = marker.publishTransRot(self.publisher)
                trans, rot = marker.getTransRot()
                found = trans is not None and rot is not None
                if found:
                    try:
                        self.publisher.publish(marker.copyTransRot(trans, rot))
                    except:
                        u=1
                    break
            if not found:
                try:
                    self.publisher.publish(Transform())
                except:
                    u = 1
    def stop(self):
        self.should_run = False



WAITING_DURATION = 1.0
def GetObstacleDistance(robotName,DefusedObstacle):
    markerNames=[52,59,70,73,16,17,18,19,20,21]
    #Dont look for an obstacle you just saw
    if DefusedObstacle in markerNames:
        markerNames.remove(DefusedObstacle)
    markerNames=[str(name) for name in markerNames]

    listener = tf.TransformListener()
    for marker_name in markerNames:
        my_frame= robotName + "/base_link"
        dest_frame="4x4_"+str(marker_name)
        try:
            print my_frame
            print dest_frame
            a = listener.waitForTransform(my_frame, dest_frame, rospy.Time(), rospy.Duration(WAITING_DURATION))
            if (a==None):
                now = rospy.Time.now()
                if(listener.waitForTransform(my_frame, dest_frame, now, rospy.Duration(WAITING_DURATION))==None):
                    (trans, rot) = listener.lookupTransform(my_frame, dest_frame, rospy.Time(0))
                    distance = math.sqrt(trans[0] ** 2 + trans[1] ** 2 + trans[2] ** 2)
                    return True,marker_name,distance
            else:
                print "TF between " + str(my_frame) +" and "+ str(dest_frame) +" is unavailable"

        except (tf.Exception,tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            print "getFreeMarkerLocation threw an error, while converting from " + str(my_frame) +" and "+ str(dest_frame)
            continue
    return False,None,None


#I must put the waitForTransform in to threads
#https://www.tutorialspoint.com/python/python_multithreading.htm
