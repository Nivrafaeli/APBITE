#!/usr/bin/python

import os


def parseln(line):
    return line.split(",")

class lineData():
    def __init__(self, text):
        self.l=parseln(text)
        titles=["original_batch","method","density","detection_ratio","Distance","Number_of_obs","73","70","52","59","16","17","18","19","20","21","target1","target2","target3"]
        self.Textdict={}
        for i in xrange(len(self.l)):
            self.Textdict[titles[i]]=self.l[i]

    def getDict(self):
        return self.Textdict

class methodCounter():
    def __init__(self,method):
        self.methodName=method
        self.DensityBins = []
        self.DensityCount = {}
        self.DetectionSum = {}
        self.AllDataByDensity = {}

    def add(self,density,detection_ratio):
        if density not in self.DensityBins:
            self.DensityBins.append(density)
            self.AllDataByDensity[density]=[]
        else:
            self.AllDataByDensity[density].append(detection_ratio)
        #calculate sum of all the detections. in order to get average later
        if density in self.DensityCount:
            self.DensityCount[density] = 1 + self.DensityCount[density]
            self.DetectionSum[density] = float(detection_ratio) + self.DetectionSum[density]
        else:
            self.DensityCount[density] = 1
            self.DetectionSum[density] = float(detection_ratio)

    def GetDetectionAverageForDansity(self, density):
        if density not in self.DensityBins:
            return " "
        else:
            a=self.DetectionSum[density]
            b=self.DensityCount[density]
            return a,b,str(self.DetectionSum[density]/self.DensityCount[density])

    def GetAlldataByDensity(self,density):
        return self.AllDataByDensity[density]

class DensitySummaryTable():
    def __init__(self):
        self.Bins = []
        self.methodCounters={}
        self.methodCounters["11"]= methodCounter("11")
        self.methodCounters["41"] = methodCounter("41")
        self.methodCounters["14"] = methodCounter("14")
        self.methodCounters["44"] = methodCounter("44")

    def AddDataPoint(self,method,density,detection_ratio):
        self.methodCounters[method].add(density,detection_ratio)

        if density not in self.Bins:
            self.Bins.append(density)

    def PrintToFile(self,FreqSummary_filename):
        fwH = open(FreqSummary_filename, 'w')
        DensityHEADER = "Density,11,41,14,44\n"
        fwH.write(DensityHEADER)
        sortedBins=sorted(self.Bins)
        for bin in sortedBins:
            textBin=str(bin)
            a,b,text11= self.methodCounters["11"].GetDetectionAverageForDansity(bin)
            print str(bin)+" 11 Sum:"+str(a)+" Count:"+str(b)
            a, b,text41 = self.methodCounters["41"].GetDetectionAverageForDansity(bin)
            print str(bin) + " 41 Sum:" + str(a) + " Count:" + str(b)
            a, b,text14 = self.methodCounters["14"].GetDetectionAverageForDansity(bin)
            print str(bin) + " 14 Sum:" + str(a) + " Count:" + str(b)
            a, b,text44 = self.methodCounters["44"].GetDetectionAverageForDansity(bin)
            print str(bin) + " 44 Sum:" + str(a) + " Count:" + str(b)
            fwH.write(textBin+","+text11+","+text41+","+text14+","+text44+"\n")
        fwH.close()

    def PopOREmpty(self,array):
        if len(array)>0:
            return array.pop()
        else:
            return ""

    def PrintToFileScatter(self, Scatter_filename):
        fwH = open(Scatter_filename, 'w')
        DensityHEADER = "Density,11,41,14,44\n"
        fwH.write(DensityHEADER)

        '''
        maximum=max(len(self.methodCounters["11"].GetAlldataByDensity(bin)),len(self.methodCounters["41"].GetAlldataByDensity(bin)),len(self.methodCounters["14"].GetAlldataByDensity(bin)),len(self.methodCounters["44"].GetAlldataByDensity(bin)))
        textBin = str(bin)
        for i in xrange(maximum):
            text11 = self.PopOREmpty(self.methodCounters["11"].GetAlldataByDensity(bin))
            text41 = self.PopOREmpty(self.methodCounters["41"].GetAlldataByDensity(bin))
            text14 = self.PopOREmpty(self.methodCounters["14"].GetAlldataByDensity(bin))
            text44 = self.PopOREmpty(self.methodCounters["44"].GetAlldataByDensity(bin))
            fwH.write(textBin + "," + text11 + "," + text41 + "," + text14 + "," + text44 + "\n")
        '''
        sortedBins = sorted(self.Bins)
        for bin in sortedBins:
            textBin = str(float(bin)+0.01)
            text11=""
            text41 = ""
            text14 = ""
            text44 = ""
            for i in xrange(len(self.methodCounters["11"].GetAlldataByDensity(bin))):
                text11 = self.PopOREmpty(self.methodCounters["11"].GetAlldataByDensity(bin))
                fwH.write(textBin + "," + text11 + "," + text41 + "," + text14 + "," + text44 + "\n")

            textBin = str(bin)
            text11 = ""
            text41 = ""
            text14 = ""
            text44 = ""
            for i in xrange(len(self.methodCounters["41"].GetAlldataByDensity(bin))):
                text41 = self.PopOREmpty(self.methodCounters["41"].GetAlldataByDensity(bin))
                fwH.write(textBin + "," + text11 + "," + text41 + "," + text14 + "," + text44 + "\n")
            textBin = str(float(bin) - 0.01)
            text11 = ""
            text41 = ""
            text14 = ""
            text44 = ""
            for i in xrange(len(self.methodCounters["14"].GetAlldataByDensity(bin))):
                text14 = self.PopOREmpty(self.methodCounters["14"].GetAlldataByDensity(bin))

                fwH.write(textBin + "," + text11 + "," + text41 + "," + text14 + "," + text44 + "\n")
            textBin = str(float(bin) + 0.02)
            text11 = ""
            text41 = ""
            text14 = ""
            text44 = ""
            for i in xrange(len(self.methodCounters["44"].GetAlldataByDensity(bin))):
                text44 = self.PopOREmpty(self.methodCounters["44"].GetAlldataByDensity(bin))
                fwH.write(textBin + "," + text11 + "," + text41 + "," + text14 + "," + text44 + "\n")

        fwH.close()

directory_firstpart = "/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/"
'''
DBfilename = "APBITE_FrequanciesDB.csv"
SummaryFilename="APBITE_Densities_Summary.csv"
'''
DBfilename = "APBITE_DescendingFrequanciesDB.csv"
SummaryFilename="APBITE_DescendingDensities_Summary.csv"

DensitySummary=DensitySummaryTable()
fr_DB = open(directory_firstpart + DBfilename, 'r')
for line in fr_DB:
    if line[0]=="b":
        l = lineData(line)
        lDict = l.getDict()
        DensitySummary.AddDataPoint(lDict["method"],lDict["density"],lDict["detection_ratio"])

DensitySummary.PrintToFile(directory_firstpart+SummaryFilename)

SummaryFilename="APBITE_DescendingScatterDensities_Summary.csv"
DensitySummary.PrintToFileScatter(directory_firstpart+SummaryFilename)