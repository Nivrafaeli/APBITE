#!/usr/bin/python

# This script is executes a roslaunch command for NUM of experiments.

import argparse, sys, os, time, signal, re, subprocess

# globals
exit_status = 0

## single handler that sets exit_status to 1 for clean abort.
def signal_handler(signal, frame):
    global exit_status
    exit_status = 1

if __name__ == "__main__":


    signal.signal(signal.SIGINT, signal_handler)
    command = "python RunExperiment_w5_param.py"
    proc1 = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    proc1.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, signal_handler)
    command = "python RunExperiment_w6_param.py"
    proc2 = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    proc2.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, signal_handler)
    command = "python RunExperiment_w2_changing_obs_params.py"
    proc3 = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    proc3.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, signal_handler)
    command = "python RunExperiment_w2_changing_target_params.py"
    proc4 = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
    proc4.send_signal(signal.SIGINT)
