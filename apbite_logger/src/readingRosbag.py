
import rosbag
bag_name="b5_exp_w2_s1_APBITE.bag"
bag = rosbag.Bag('b5_w2_s1_APBITE.bag')
#for topic, msg, t in bag.read_messages(topics=['chatter', 'numbers']):
for topic, msg, t in bag.read_messages():
    print msg
bag.close()


#bag_name="/media/lizi-lab/storage/apbite_experiments/batch5_bags/b5_exp_w2_s1_APBITE.bag.active"
'''
outputBag_name=bag_name+"_Out"
with rosbag.Bag(outputBag_name, 'w') as outbag:
    for topic, msg, t in rosbag.Bag(outputBag_name).read_messages():
        # This also replaces tf timestamps under the assumption
        # that all transforms in the message share the same timestamp
        if topic == "/tf" and msg.transforms:
            outbag.write(topic, msg, msg.transforms[0].header.stamp)
        else:
            outbag.write(topic, msg, msg.header.stamp if msg._has_header else t)

'''