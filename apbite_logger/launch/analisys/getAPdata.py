#!/usr/bin/python

import os
import argparse, sys, os, time, signal, re, subprocess


command1 = "rostopic"
command2= "echo"
command3="-b"
bagfile = "/media/lizi-lab/storage/apbite_experiments/batch9_bags/b9_exp_w2_s1_APBITE.bag.active"
topic="/bite/lizi_1/knowledge_update"

import rosbag

bag = rosbag.Bag(bagfile)
messages=filter(lambda x: x.message, bag.read_messages(["/bite/lizi_1/knowledge_update"]))
for msg in messages:
    if "AP_STATUS" in msg.message.data:
        str=msg.message.data.replace("AP_mb_list:","")
        str = str.replace("AP_STATUS", "")
        str = str.replace("AP_mb_list:", "")
        str = str.replace("Chosen_mb_toSolve:", "")
        str = str.replace("Status:", "")
        str = str.replace("|", "")
        list,chosen,status=str.split(",")
        print msg.message.header.stamp.to_sec(), "[", list,"]",chosen,status
