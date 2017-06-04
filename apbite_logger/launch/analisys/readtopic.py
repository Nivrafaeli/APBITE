#!/usr/bin/python

import os.path, subprocess, re,math

class messege(object):
    def __init__(self,text):
        self.alldata=[]
        self.secs=""
        self.nsecs=""
        self.data=""
        try:
            if text == "":
                pass
            else:
                text = text.split("\n")
                data=[]
                for line in text:
                    line=line.replace(' ','')
                    line=line.split(":")
                    self.alldata.append(line)
                for line in self.alldata:
                    if line [0]=="secs":
                        self.secs=line[1]
                    if line[0] =="nsecs":
                        self.nsecs=line[1]
                    if line[0]=="data":
                        self.data=line[1:]
        except:
            pass

    def getinfo(self):
        strdata=""
        for d in self.data:
            strdata= strdata + ","+str(d)
        strdata=strdata+"\n"
        return self.secs+"," +self.nsecs+ "," + strdata

    def getsubject(self):
        strdata = ""
        for d in self.data:
            strdata = strdata + "," + str(d)
        strdata = strdata + "\n"
        return strdata

#*****************************************************
#These are the parameters
bag="b12_exp_w4_s0_APBITE_1.0_1.0"
batch="12"
#The file will appear in the experiments folder
#*****************************************************

os.environ["PYTHONPATH"] = "/home/lizi-lab/catkin_ws/devel/lib/python2.7/dist-packages:/opt/ros/kinetic/lib/python2.7/dist-packages"
os.environ["PATH"] += ":/home/lizi-lab/catkin_ws/devel/bin:/opt/ros/kinetic/bin:/home/lizi-lab/.local/share/umake/bin:/home/lizi-lab/bin:/home/lizi-lab/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/.local/bin"

command1="/opt/ros/kinetic/bin/rostopic echo /bite/lizi_1/knowledge_update -b /home/lizi-lab/storage/apbite_experiments/batch"+batch+"_bags/"



command2=".bag.active"
command=command1+bag+command2
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)


struct = proc.stdout.read()
struct =struct.split("---")

a=[messege(s) for s in struct]


directory = os.path.join("","/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/batch"+batch+"/")
summary_filename = "KnowledgeTopic_"+bag+".csv"
SummaryHEADER = "secs, nsecs, belief, value\n"
with open(directory+summary_filename, 'w') as fw:
        fw.write(SummaryHEADER)
        downtime = []
        uptime = []
        downtimestop = []
        uptimestop = []
        for msg in a:
            line= msg.getinfo()
            print line
            fw.write(line)
            subject=msg.getsubject()
            subject=subject.replace(',','')
            subject=subject.replace('\n', '')
            nsecs=msg.nsecs
            secs=msg.secs
            try:
                time=float(secs)+float(nsecs) * math.pow(10, -len(nsecs))
            except:
                pass
            if subject=="CameraDownTrue":
                downtime.append(time)
            if subject=="CameraUpTrue":
                uptime.append(time)
            if subject=="CameraDownFalse":
                downtimestop.append(time)
            if subject=="CameraUpFalse":
                uptimestop.append(time)
        i=0
        sumdown=0.0
        for d in downtime:
            try:
                sumdown=sumdown+downtimestop[i]-downtime[i]
                i=i+1
            except:
                pass
        j = 0
        sumup = 0.0
        for u in uptime:
            try:
                sumup = sumup + uptimestop[j] - uptime[j]
                j = j + 1
            except:
                pass

        fw.write("Down time: , "+str(sumdown)+"\n")
        fw.write("Up time: , "+str(sumup)+"\n")
