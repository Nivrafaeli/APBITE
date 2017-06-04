#!/usr/bin/python

import os


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

class methodCounter():
    def __init__(self,method):
        self.methodName=method
        self.methodBins = []
        self.methodCount = {}
        self.methodSum = 0.0

    def add(self,obs_ratio):
        if obs_ratio not in self.methodBins:
            self.methodBins.append(obs_ratio)

        if obs_ratio in self.methodCount:
            self.methodCount[obs_ratio] = 1 + self.methodCount[obs_ratio]
        else:
            self.methodCount[obs_ratio] = 1

        self.methodSum = self.methodSum+1

    def GetRatioOfBin(self, obs_ratio):
        if obs_ratio not in self.methodBins:
            return "0.0"
        else:
            return str(self.methodCount[obs_ratio]/self.methodSum)

class HistogramDataClass():
    def __init__(self):

        self.Bins = []
        self.methodCounters={}
        self.methodCounters["11"]= methodCounter("11")
        self.methodCounters["41"] = methodCounter("41")
        self.methodCounters["14"] = methodCounter("14")
        self.methodCounters["44"] = methodCounter("44")

    def AddDataPoint(self,method,obs_ratio):
        self.methodCounters[method].add(obs_ratio)

        if obs_ratio not in self.Bins:
            self.Bins.append(obs_ratio)

    def PrintToFile(self,Histogram_filename):
        fwH = open(Histogram_filename, 'w')
        HistogramHEADER = "Bin,11,41,14,44\n"
        fwH.write(HistogramHEADER)

        sortedBins=sorted(self.Bins)
        for bin in sortedBins:
            textBin=str(bin)
            text11= self.methodCounters["11"].GetRatioOfBin(bin)
            text41 = self.methodCounters["41"].GetRatioOfBin(bin)
            text14 = self.methodCounters["14"].GetRatioOfBin(bin)
            text44 = self.methodCounters["44"].GetRatioOfBin(bin)
            fwH.write(textBin+","+text11+","+text41+","+text14+","+text44+"\n")
        fwH.close()

directory_firstpart="/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/"

'''
def createDb(relevantbachnumbers,DBfilename):
    filename=DBfilename
    fwH = open(directory_firstpart + filename, 'w')
    DBHeader = "Batch, World, Method, Experiment, #obstacles passed, #obstacles identified, #targets passed, #targets identified,73,70,52,59,16,17,18,19,20,21,target1,target2,target3\n"
    fwH.write(DBHeader)
    for batchNum in relevantbachNumbers:
        directory_secondpart="batch"+str(batchNum)+"/"
        directory = os.path.join(directory_firstpart,directory_secondpart)

        for root,dirs,files in os.walk(directory):
            for file in files:
                if file.endswith("SummaryData.csv"):
                    fr=open(directory+file, 'r')
                    for line in fr:
                        if line.startswith("b"+str(batchNum)):
                            l=lineData(line)
                            lDict= l.getDict()
                            fwH.write(line)
  '''

for i in xrange(5):
    if i ==0:
        relevantbachNumbers=[9,10,11]
        Histogram_filename="/Histograms/Histogram_10obs_9meter.csv"
    if i == 1:
        relevantbachNumbers=[12,13,16,17,19]
        Histogram_filename="/Histograms/Histogram_10obs_12meter.csv"
    if i == 2:
        relevantbachNumbers=[14,15,20,21,23]
        Histogram_filename="/Histograms/Histogram_3obs_95meter.csv"
    if i == 3:
        relevantbachNumbers=[9,10,11,12,13,16,17,19]
        Histogram_filename="/Histograms/Histogram10Obstacles.csv"
    if i == 4:
        relevantbachNumbers=[9,10,11,12,13,14,15,16,17,19,20,21,23]
        Histogram_filename="/Histograms/HistogramAll.csv"


    DBfilename = "AllBatchesDB.csv"
    fwH=open(directory_firstpart+DBfilename, 'w')
    DBHeader = "Batch, World, Method, Experiment, #obstacles passed, #obstacles identified, #targets passed, #targets identified,73,70,52,59,16,17,18,19,20,21,target1,target2,target3\n"
    fwH.write(DBHeader)

    analysis_filename = "APBITE_Clean_ratios.csv"


    AnalysisHEADER = "Index , method, Obs ratio, Target ratio\n"
    fwA=open(directory_firstpart+analysis_filename, 'w')
    #fwA.write(AnalysisHEADER)


    HistogramData=HistogramDataClass()
    for batchNum in relevantbachNumbers:
        directory_secondpart="batch"+str(batchNum)+"/"
        directory = os.path.join(directory_firstpart,directory_secondpart)

        for root,dirs,files in os.walk(directory):
            for file in files:
                if file.endswith("SummaryData.csv"):
                    fr=open(directory+file, 'r')
                    #FileInstance=fileData(file)
                    #  perform calculation
                    for line in fr:
                        if line.startswith("b"+str(batchNum)):
                            l=lineData(line)
                            lDict= l.getDict()
                            #fwH.write(line)
                            if lDict["target1"]=="O":
                                #get ride of all the trys that didnt reached to target
                                print line
                            else:
                                fwH.write(line)
                                method=lDict["Method"]
                                #copy only APBITE
                                if method[0]=="A":
                                    if method=="APBITE 1.0-1.0":
                                        methodName="11"
                                    if method=="APBITE 4.0-4.0":
                                        methodName="44"
                                    if method=="APBITE 1-4.0" or method=="APBITE 1.0-4.0" :
                                        methodName="14"
                                    if method == "APBITE 4.0-1" or method == "APBITE 4.0-1.0":
                                        methodName = "41"
                                    index=lDict["Batch"]+"_"+lDict["Experiment"]+"_"+methodName
                                    obs_passed=float(lDict["#obstacles passed"])
                                    obs_saw=float(lDict["#obstacles identified"])
                                    target_passed=float(lDict["#targets passed"])
                                    target_saw=float(lDict["#targets identified"])

                                    if obs_passed==0:
                                        obs_ratio=0.0
                                    else:
                                        obs_ratio=obs_saw/obs_passed

                                    if target_passed==0:
                                        target_ratio=0.0
                                    else:
                                        target_ratio = target_saw/ target_passed
                                    fwA.write(index+","+methodName+","+str(obs_ratio)+","+str(target_ratio)+"\n")

                                    HistogramData.AddDataPoint(methodName,obs_ratio)


    HistogramData.PrintToFile(directory_firstpart+Histogram_filename)
    fwH.close()
    fwA.close()

