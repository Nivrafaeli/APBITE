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
    NUM = 10
    arg_batch_number="3"
    arg_number_of_targets= "3"
    arg_world= "1"
    arg_method= "APBITE"
    #Only one of the following should be true
    arg_APBITE= "true"
    arg_opt= "false"
    arg_lookup = "false"
    arg_lookdown= "false"
    command = "roslaunch RunExpermints.launch"

    params=           " batch_number:="+arg_batch_number
    params = params + " number_of_targets:="+arg_number_of_targets
    params = params + " world:=" + arg_world
    params = params + " method:=" + arg_method
    params = params + " APBITE:=" + arg_APBITE
    params = params + " opt:=" + arg_opt
    params = params + " lookup:=" + arg_lookup
    params = params + " lookdown:=" + arg_lookdown
    params = params + " world"+str(arg_world)+":=true" #This parameter detarmins which world will be launched

    signal.signal(signal.SIGINT, signal_handler)
    i=1
    while i < NUM+1 and exit_status==0:
        if not exit_status == 0: break
        arg_serial_num = i
        params2 = params + " serial_num:=" + str(i)
        command1=command+params2
        print command1
        proc = subprocess.Popen(command1, shell=True, preexec_fn=os.setsid)
        if arg_world=="1":
            time.sleep(200)
        proc.send_signal(signal.SIGINT)
        kill_command = """kill -9 `ps aux | grep [r]os | awk '{print $2}'`"""
        proc.send_signal(signal.SIGKILL)
        time.sleep(5)
        proc = subprocess.Popen(kill_command, shell=True, preexec_fn=os.setsid)
        time.sleep(10)
        i=i+1

    sys.exit(exit_status)
