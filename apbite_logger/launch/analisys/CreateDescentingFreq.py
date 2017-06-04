#!/usr/bin/python

import os

#look only on batch numbers with 10 obstacles
RELEVANTBATCHNUMBERS=[9,10,11,12,13,16,17,19]

def parseln(line):
    return line.split(",")

class lineData():
    def __init__(self, text):
        self.l=parseln(text)
        titles=["Batch", "World", "Method", "Experiment", "#obstacles passed", "#obstacles identified", "#targets passed", "#targets identified","73","70","52","59","16","17","18","19","20","21","target1","target2","target3"]
        self.Textdict={}
        for i in xrange(len(self.l)):
            self.Textdict[titles[i]]=self.l[i]

    def getDict(self):
        return self.Textdict


class CreateFrequancies():
    def __init__(self, directory_firstpart, Freqfilename):
        self.fw_frequancies = open(directory_firstpart + Freqfilename, 'w')
        # DBHeader = "Batch, World, Method, Experiment, #obstacles passed, #obstacles identified, #targets passed, #targets identified,73,70,52,59,16,17,18,19,20,21,target1,target2,target3\n"
        fr_DB_Header = "original_batch,method,density,detection_ratio,Distance,Number_of_obs,73,70,52,59,16,17,18,19,20,21,target1,target2,target3\n"
        self.fw_frequancies.write(fr_DB_Header)

    def fileclose(self):
        self.fw_frequancies.close()

    def getmethod(self,method):
        if method == "APBITE 1.0-1.0":
            methodName = "11"
        if method == "APBITE 4.0-4.0":
            methodName = "44"
        if method == "APBITE 1-4.0" or method == "APBITE 1.0-4.0":
            methodName = "14"
        if method == "APBITE 4.0-1" or method == "APBITE 4.0-1.0":
            methodName = "41"
        return methodName

    def getDistance(self,world):
        distance="0"
        if world =="w2":
            distance = "9"
        if world =="w3":
            distance = "9.5"
        if world =="w4":
            distance = "12"
        return distance

    def addFreq(self, lDict,ignor_num_of_obs):
        methodName=self.getmethod(lDict["Method"])
        original_batch = lDict["Batch"] + "_" + lDict["Experiment"] + "_" + methodName
        distance_str=self.getDistance(lDict["World"])
        distance=float(distance_str)

        import itertools
        ObsNames=["73","70","52","59","16","17","18","19","20","21"]
        AllObsNames=["73","70","52","59","16","17","18","19","20","21"]
        obs_num=10-ignor_num_of_obs
        Number_of_obs=str(obs_num)
        density=str(float(obs_num)/distance)

        #ignore some of the obstacles
        import random
        for i in xrange(ignor_num_of_obs):
            ObsNames.pop(random.randint(0, len(ObsNames) - 1))
        detection=0.0
        #Count the number of detections
        for obs in ObsNames:
            if lDict[obs]=="V":
                detection=detection+1.0
        detection_ratio=str(detection/float(obs_num))
        text_firstpart=original_batch+","+methodName+","+density+","+detection_ratio+","+distance_str+","+Number_of_obs
        text_secondpart=""
        for obs in AllObsNames:
            if obs in ObsNames:
                text_secondpart=text_secondpart+","+lDict[obs]
            else:
                text_secondpart = text_secondpart + ","
        text = text_firstpart+text_secondpart + ","+lDict["target1"]+","+lDict["target2"]+","+lDict["target3"]

        self.fw_frequancies.write(text)

directory_firstpart = "/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/"
DBfilename = "AllBatchesDB.csv"

FreqCreator=CreateFrequancies(directory_firstpart,"APBITE_DescendingFrequanciesDB.csv")

ignor_nub_of_obs=-1
for batchNum in RELEVANTBATCHNUMBERS:
    ignor_nub_of_obs =ignor_nub_of_obs+1
    fr_DB = open(directory_firstpart + DBfilename, 'r')
    for line in fr_DB:
        print str(line)
        t1= line[0:line.find(",")]
        t2="b"+str(batchNum)
        print ("t1: "+t1+" t2: "+t2 )
        if t1==t2:

        #if line.startswith("b"+str(batchNum)):
            l=lineData(line)
            lDict= l.getDict()
            #fwH.write(line)
            method=lDict["Method"]
            #send to freq  only APBITE
            if method[0]=="A":

                FreqCreator.addFreq(lDict,ignor_nub_of_obs)
    fr_DB.close()

FreqCreator.fileclose()
