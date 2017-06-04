#!/usr/bin/python

import os
import math

BATCHNUM="23"

def parseln(line):
    return line.split(",")

DISTANCEFROMREALALLOWED=0.33

class fileData(object):
    def __init__(self, filename):
        file_details=filename.split("_")

        self.batch=file_details[0]
        self.world=file_details[2]

        self.serialNum=file_details[3]
        self.method = file_details[4]
        self.secs_to_miss_ObstacleOnTheWay = file_details[5]
        self.secs_to_miss_KnowsTargetLocation = file_details[6].replace(".csv","")
        self.obs_passed={}
        self.target_passed = {}
        self.obs_seen = {}
        self.target_seen = {}

class Data(object):
    def __init__(self,line):
        line=line.replace(" ","")
        text = line.split(",")
        self.report_type = text[1]
        self.object_type=""
        if "Obstacletarget" in text[2] or "TargetReached" in text[2]:
            self.object_type="Target"
        elif "myObstacle" in text[2] or "Obstacle" in text[2]:
            self.object_type="Obstacle"
        else:
            pass

        text[2]=text[2].replace("Obstacletarget","")
        text[2] =text[2].replace("TargetReached", "")
        text[2] =text[2].replace("myObstacle","" )
        text[2] =text[2].replace("Obstacle","")
        self.object_num=text[2]

        #if(self.report_type)==" 0":
        if (self.report_type) == "0":
            self.distance_from_real = None
        else:
            a=text[7]
            ab = text[6]
            self.distance_from_real = float(text[7])-float(text[6])


    def GetObject_type(self):
        if self.object_type=="Obstacle":
            return "Obstacle"
        else:
            return "Target"

    def GetReport_type(self):
        #if self.report_type==" 0":
        if self.report_type == "0":
            return "real"
        else:
            return "robot"

    def GetDistanceFromReal(self):
        return self.distance_from_real

    def IsItReal(self):
        if abs(self.distance_from_real)<DISTANCEFROMREALALLOWED:
            return True
        else:
            return False

directory = os.path.join("","/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/batch"+BATCHNUM+"/")
summary_filename = "SummaryData.csv"
SummaryHEADER = "Batch, World, Method, Experiment, #obstacles passed, #obstacles identified, #targets passed, #targets identified,73,70,52,59,16,17,18,19,20,21,target1,target2,target3\n"
with open(directory+summary_filename, 'w') as fw:
        fw.write(SummaryHEADER)

allFiles=[]
for root,dirs,files in os.walk(directory):

    for file in files:
        if file.endswith(".csv") and not file.endswith("marker_locations.csv") and not file.endswith("SummaryData.csv"):
            fr=open(directory+file, 'r')
            FileInstance=fileData(file)
            #  perform calculation
            for line in fr:
                if line.startswith(" time"):
                    pass
                else:

                    temp_d=Data(line)
                    if temp_d.GetReport_type()=="real":
                        ty=temp_d.GetObject_type()
                        if temp_d.GetObject_type()=="Obstacle":
                            FileInstance.obs_passed[temp_d.object_num]=True
                        else:
                            FileInstance.target_passed[temp_d.object_num] = True
                    else:
                        if temp_d.IsItReal()==True:
                            if temp_d.GetObject_type() == "Obstacle":
                               FileInstance.obs_seen[temp_d.object_num] = True
                            else:
                               FileInstance.target_seen[temp_d.object_num] = True
                            '''
                            #If the agent sees a target, it marked also as passing next to it
                               t=FileInstance.target_passed[temp_d.object_num]
                               if t is True:
                                   pass
                               else:
                                   FileInstance.target_passed[temp_d.object_num] = True
                                '''
            fr.close()
            allFiles.append(FileInstance)

    fw = open(directory + summary_filename, 'a')

    class typeSummary(object):
        def __init__(self,type):
            self.type=type
            self.sumOfobs_passed=0.0
            self.sumOfobs_seen = 0.0
            self.sumOfTarget_passed = 0.0
            self.sumOfTarget_seen = 0.0
            self.obsRatio=0.0
            self.TargetRatio=0.0


        def update(self,NumOfobs_passed,NumOfobs_seen,NumOfTarget_passed,NumOfTarget_seen):
            self.sumOfobs_passed = self.sumOfobs_passed +NumOfobs_passed
            self.sumOfobs_seen = self.sumOfobs_seen+NumOfobs_seen
            self.sumOfTarget_passed = self.sumOfTarget_passed+NumOfTarget_passed
            self.sumOfTarget_seen = self.sumOfTarget_seen+NumOfTarget_seen
            if self.sumOfobs_passed==0.0:
                self.obsRatio=0.0
            else:
                self.obsRatio = self.sumOfobs_seen/self.sumOfobs_passed

            if self.sumOfTarget_passed==0:
                self.TargetRatio=0.0
            else:
                self.TargetRatio = self.sumOfTarget_seen/self.sumOfTarget_passed

    typeSummaries=[]
    types=["opt","APBITE 4.0-1.0","APBITE 1.0-1.0","APBITE 4.0-4.0","APBITE 1.0-4.0","lookup","lookdown"]
    obs_list=["73","70","52","59","16","17","18","19","20","21"]
    target_list=["1","2","3"]
    for t in types:
        tS = typeSummary(t)
        for f in allFiles:
            if f.method == "APBITE":
                params = " " + str(f.secs_to_miss_ObstacleOnTheWay) + "-" + str(f.secs_to_miss_KnowsTargetLocation)
            else:
                params = ""
            method = str(f.method)+params
            print t
            print method
            if method==t:
                NumOfobs_passed=len(f.obs_passed)
                NumOfobs_seen=len(f.obs_seen)
                NumOfTarget_passed=len(f.target_passed)
                NumOfTarget_seen=len(f.target_seen)

                line=f.batch+","+f.world+","+method+","+f.serialNum+","+str(NumOfobs_passed)+","+str(NumOfobs_seen)+","+str(NumOfTarget_passed)+","+str(NumOfTarget_seen)
                for obs in obs_list:
                    if obs in f.obs_passed:
                        if obs in f.obs_seen:
                            line=line+","+"V"
                        else:
                            line = line + "," + "X"
                    else:
                        line = line + "," + "O"

                for target in target_list:
                    if "Targettarget"+str(target) in f.target_passed:
                        if target in f.target_seen:
                            line=line+","+"V"
                        else:
                            line = line + "," + "X"
                    else:
                        line = line + "," + "O"
                fw.write(line+"\n")

                tS.update(NumOfobs_passed,NumOfobs_seen,NumOfTarget_passed,NumOfTarget_seen)
        typeSummaries.append(tS)

    line="\n"
    for i in xrange(5):
        fw.write(line)
    fw.write("Type,Sum(Obs_Passes),Sum(Obs_seen),Obs Ratio, ,Sum(Target_Passed),Sum(Target_seen),Target Ratio\n")

    for tS in typeSummaries:
        line = str(tS.type) +","+str(tS.sumOfobs_passed)+","+str(tS.sumOfobs_seen)+","+str(tS.obsRatio)+","+","+str(tS.sumOfTarget_passed)+","+str(tS.sumOfTarget_seen)+","+str(tS.TargetRatio)+"\n"
        fw.write(line)

    fw.close()