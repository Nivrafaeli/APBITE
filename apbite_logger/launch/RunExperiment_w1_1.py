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
    NUM = 20
    arg_batch_number="8"
    arg_number_of_targets= "3"
    arg_world= "1"
    command = "roslaunch RunExpermints.launch"
    signal.signal(signal.SIGINT, signal_handler)
    batch_location = "/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/batch"+str(arg_batch_number) + "/marker_locations.csv"
    fb = open(batch_location, 'a')
    fb.write("\n*****,*****,*****,*****,******,*****,*****,*****")
    fb.close()

    i=0
    while i < NUM+1 and exit_status==0:
        if not exit_status == 0: break
        #1.create world
        arg_serial_num = i

        create_world_command = "python random_obstacles_w1.py batch"+str(arg_batch_number)+" "+arg_world +" "+str(arg_serial_num)
        proc = subprocess.Popen(create_world_command, shell=True, preexec_fn=os.setsid)
        #2. run 4 times change methods
        j=0
        while j < 4 and exit_status==0:
            if not exit_status == 0: break
            #remove
            if j == 0:
                arg_method = "APBITE"
                arg_APBITE = "true"
                arg_opt = "false"
                arg_lookup = "false"
                arg_lookdown = "false"
            if j == 1:
                arg_method = "opt"
                arg_APBITE = "false"
                arg_opt = "true"
                arg_lookup = "false"
                arg_lookdown = "false"
            if j == 2:
                arg_method = "lookup"
                arg_APBITE = "false"
                arg_opt = "false"
                arg_lookup = "true"
                arg_lookdown = "false"
            if j == 3:
                arg_method = "lookdown"
                arg_APBITE = "false"
                arg_opt = "false"
                arg_lookup = "false"
                arg_lookdown = "true"
            params = " serial_num:=" + str(i)
            params = params + " batch_number:=" + arg_batch_number
            params = params + " number_of_targets:=" + arg_number_of_targets
            params = params + " world:=" + arg_world
            params = params + " method:=" + arg_method
            params = params + " APBITE:=" + arg_APBITE
            params = params + " opt:=" + arg_opt
            params = params + " lookup:=" + arg_lookup
            params = params + " lookdown:=" + arg_lookdown
            params = params + " world" + str(arg_world) + ":=true"  # This parameter detarmins which world will be launched

            #3. kill experinment
            if not exit_status == 0: break
            command1 = command + params
            print command1
            proc = subprocess.Popen(command1, shell=True, preexec_fn=os.setsid)
            if arg_world == "1":
                time.sleep(200)
            if arg_world == "2":
                time.sleep(120)
            if arg_world == "3":
                time.sleep(120)
            proc.send_signal(signal.SIGINT)
            kill_command = """kill -9 `ps aux | grep [r]os | awk '{print $2}'`"""
            proc.send_signal(signal.SIGKILL)
            time.sleep(5)
            proc = subprocess.Popen(kill_command, shell=True, preexec_fn=os.setsid)
            time.sleep(10)
            j=j+1
            # remove
            #j=4
        #4. change serial
        i = i + 1






    sys.exit(exit_status)
