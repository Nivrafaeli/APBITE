#!/usr/bin/python

import random,sys
from time import gmtime, strftime

def good_distance(locations, this_location):
    for location in locations:
        distance=abs(location-this_location)
        if distance<0.2:
            return False
    return True

if __name__ == "__main__":
    #batchname="batch3"
    batchname=sys.argv[1]
    batch_location="/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/"+batchname+"/marker_locations.csv"
    fb = open(batch_location, 'a')

    # 10 obstacles
    world_num = sys.argv[2]
    # 3 obstacles
    serial_num = sys.argv[3]
    #master_filename = "/home/lizi-lab/Dropbox/BITE_DROPBOX/bite_drive_between_targets/launch/Worlds/world2_master.txt"

    master_filename = "/home/lizi-lab/Dropbox/BITE_DROPBOX/bite_drive_between_targets/launch/Worlds/world"+world_num+"_master.txt"
    fr = open(master_filename, 'r')

    new_filename = "/home/lizi-lab/Dropbox/BITE_DROPBOX/bite_drive_between_targets/launch/Worlds/world_"+world_num+".launch"
    fw = open(new_filename, 'w')

    part1="\t<node name=\"spawn_urdf"
    part2="\" pkg=\"gazebo_ros\" type=\"spawn_model\"  args=\"-file $(find bite_drive_between_targets)/urdf/free_marker_"
    part3=".urdf -urdf   -x "
    part4=" -y -0.0 -z 0 -Y 0 -model free_marker_"
    part5="\" />\n"
    fb.write(strftime("\n"+serial_num+","+"%Y-%m-%d %H:%M:%S", gmtime())+", ")
    locations=[]
    for line in fr:
        if line[0]=="@":
            words=line[:-1].split(" ")
            good_dist=False
            while not good_dist:
                random_location=round(random.random()*4.7+1.0,2)
                good_dist=good_distance(locations,random_location)
            locations.append(random_location)
            marker_name=words[1]
            fw.write(part1+marker_name+part2+marker_name+part3+ str(random_location)+part4+ marker_name+part5)
            fb.write(marker_name+","+str(random_location)+",")
        else:
            fw.write(line)
    fr.close()
    fw.close()
    fb.close()
