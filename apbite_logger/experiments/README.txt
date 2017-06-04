
15 experiments
7 types of algorithms
lookup, lookdown, opt, APBITE 1 4, APBITE 1 1, APBITE 4 1, APBITE 4 4
	where APBITE x y stands for:
		x = The time in seconds passes until knowsObject turns to be missing
		y = The time in seconds passes until knowsTargetLocation turns to be missing

batch 9  , batch 10 ,batch 11 (RunExperiment_w2_param.py) 9 meter 10 obs
batch 12 , batch 13 (RunExperiment_w4_param.py) 12 meter 10 obs
batch 14 , batch 15 (RunExperiment_w3_param.py) 9.5 meter 3 obs
batch 16 , batch 17 , batch 19 (RunExperiment_w4_param.py) 12 meter 10 obs
batch 20 , batch 21 , batch 23 (RunExperiment_w3_param.py) 9.5 meter 3 obs

b24 25 26 27 28 - density 0.6 (RunExperiment_w5_param.py)
b29 30 31 32 33- density 1.5 (RunExperiment_w6_param.py)
b34 35 36 37 38- changing param (RunExperiment_w2_changing_obs_param.py)
b39 40 41 42 43- changing param (RunExperiment_w2_changing_target_param.py)

I want to use then in order to create different frequancies graphs



Data extraction
---------------
1- Running an experiment: python RunExperiment_wX_param.py
2- Collecting data using: collectDataParams.py - Have to change batch number in the file
3- Creating the csv files in Histogram folder: UniteAllBaches.py 
   Creates also Database for all the relevant batches: AllBatchesDB.csv

4- FrequancyAnalysis.py using  AllBatchesDB.csv in order to create larger DB of all frequancies
5- ReadFrequancyDB.py
