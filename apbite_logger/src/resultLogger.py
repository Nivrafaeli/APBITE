#!/usr/bin/python

import rospy
import sys
from apbite_logger.msg import loggerMessage
from std_msgs.msg import String


class Logger:
    def __init__(self, filename,logger_summary_file_name,experiment_name,number_of_targets,method):
        self.experiment_name=experiment_name
        self.filename = filename
        self.number_of_targets=number_of_targets
        self.method=method
        HEADER=" time, 0-real 1-robot,object type,agent to obs x(robot),agent to obs y(robot),agent to obs z(robot), distance(robot),distance(real), sus obs x(robot), sus obs y(robot),sus obs z(robot), obs x(real), obs y(real), obs z(real), robot x(real), robot y(real), robot z(real)\n"
        with open(filename, 'w') as fd:
            fd.write(HEADER)

    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def roundNums(self,sentance):

        list=sentance.split(",")
        word=list[0]
        rest=list[1:]
        #rest = [round(float(x), 2) for x in list[1:] if self.is_number(x)]
        ans=word

        for w in rest:
            if self.is_number(w):
                ans = ans + "," +str(round(float(w), 2))
            else:
                ans=ans+","+str(w)


        return ans


    def output_to_file(self, msg):
        type=msg.object_name.split(" ")[0]
        source=msg.distance
        time=msg.time_stamp.to_sec()
        roundnumb=self.roundNums(msg.object_name)
        #line = "%f, %d, %s " % (msg.time_stamp.to_sec(),msg.distance,msg.object_name)
        line = "%f, %d, %s " % (msg.time_stamp.to_sec(), msg.distance, roundnumb)
        with open(self.filename, 'a') as fd:
            fd.write(line + "\n")



class robotMeasurmentPublisher(object):

    def __init__(self, publish_topic_name, robot_name, logger_file_name,logger_summary_file_name,experiment_name,number_of_targets,method):
        self.robot_name = robot_name
        self.topic_name = topic_name
        self.number_of_targets = number_of_targets
        self.logger = Logger(logger_file_name,logger_summary_file_name,experiment_name,number_of_targets,method)

        # wait for gazebo to start publishing states before attaching a listener to the topic
        try:
            self.callback(rospy.wait_for_message(self.topic_name, loggerMessage))
        except rospy.ROSInterruptException:
            sys.exit("Received shutdown signal...")
        self.listener = rospy.Subscriber(self.topic_name, loggerMessage, self.callback)

    def callback(self, msg):
        self.logger.output_to_file(msg)




if __name__=="__main__":
    rospy.init_node("result_logger")
    logger_file_name = rospy.get_param("~file_name")
    number_of_targets = rospy.get_param("~number_of_targets")
    method = rospy.get_param("~method")
    experiment_name = rospy.get_param("~experiment_name")
    logger_summary_file_name=logger_file_name+"_summary"
    robot_name = rospy.get_param("~robot_name")
    topic_name = "results_%s" % robot_name
    robotMeasurmentPublisher(topic_name, robot_name, logger_file_name,logger_summary_file_name,experiment_name,number_of_targets,method)
    rospy.spin()
