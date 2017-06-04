#!/usr/bin/python

import os
def getObservedMarkers(file_path):
    fr = open(file_path, 'r')
    opt_truemarkers = {}
    for line in fr:
        words = line.split(",")
        if "Obstacle f" in words[0]:
            marker = words[0][-2:]
            time = float(words[2])
            opt_truemarkers[time]= marker
    fr.close()

    opt_noticed_markers={}
    fr = open(file_path, 'r')
    for line in fr:
        words = line.split(",")
        if "Obstacle" in words[0] and not "Obstacle f" in words[0]:
            closest_marker = min(opt_truemarkers, key=lambda x: abs(x - float(words[2])))
            opt_noticed_markers[opt_truemarkers[closest_marker]] ="1"
    fr.close()
    return opt_noticed_markers

if __name__ == "__main__":
    directory = os.path.join("","/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/batch4/")
    results_filename = "apbiteVSopt.csv"

    resultsHEADER = "Serie, makrer, location, opt, apbite\n"
    fd= open(directory+results_filename, 'w')
    fd.write(resultsHEADER)
    s=1
    f_ml = open(directory+"marker_locations.csv", 'r')
    for line in f_ml:
        line = line[:-1]
        words=line.split(",")
        num_of_obs=(len(words)-1)/2
        obs_dict = {}
        for i in xrange(num_of_obs):
            obs_dict[words[1+2*i]]=words[2+2*i]

        try:
            f_opt=directory+"b4_exp_w2_s"+str(s)+"_opt.csv"
            opt_observed = getObservedMarkers(f_opt)
        except:
            s = s + 1
            continue

        try:
            f_apbite = directory + "b4_exp_w2_s" + str(s) + "_APBITE.csv"
            apbite_observed = getObservedMarkers(f_apbite)
        except:
            s = s + 1
            continue

        for obs in obs_dict:
            fd.write(str(s)+","+obs+","+obs_dict[obs]+",")
            if obs in opt_observed:
                fd.write("1,")
            else:
                fd.write("0,")
            if obs in apbite_observed:
                fd.write("1\n")
            else:
                fd.write("0\n")
        s=s+1
    fd.close()
    f_ml.close()
