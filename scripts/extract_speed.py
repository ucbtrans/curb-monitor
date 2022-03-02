from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import os, sys, shutil
import subprocess
import string
from get_gps_metadata import *
from datetime import datetime
from functools import cmp_to_key

"""
Shattuk ending pt: 37.867615, -122.267864 .266 to .268
Shattuk start pt: 37.868658, -122.259921 .25994 to .25999 

Bus stop end pt: 37.868658, -122.259921    .259 to .25993
Bus stop start pt: 37.868985, -122.257163  time stamp: 2:22:38 .25718 to .2572

College Ave start pt: 37.869305, -122.254609   from .253 to .2555
College Ave end pt: Bus stop start pt: 37.868985, -122.257163 .256 .25717

"""

def assign_endpoint_str(long, lat):
    if long > 122.253 and long < 122.255 and lat > 37.8692  and lat < 37.8693:
        return "CAS"
    elif long > 122.2567 and long < 122.257:
        return "CAE"
    elif long > 122.25718 and long < 122.2572:
        return "BSS"
    elif long > 122.259 and long < 122.25994:
        return "BSE"
    elif long > 122.25994 and long < 122.25999:
        return "SHS"
    elif long > 122.266 and long < 122.268:
        return "SHE"
    return None

def comp_tuples(loc1, loc2):
    # print(loc1[0])
    # print(loc2[0])
    if loc1[0] < loc2[0]:
        return -1
    elif loc1[0] > loc2[0]:
        return 1
    else:
        return 0

def calculate_avg_spd(loc_list):
    segment_lookup = {"College Ave": [], "Bus Stop": [], "Shattuck": []}
    loc_order = ["CAS", "CAE", "BSS", "BSE", "SHS", "SHE"]
    for i in range(1, len(loc_list)):
        if loc_list[i] == "CAS":
            continue
        curr_loc_ind = loc_order.index(loc_list[i][2])
        if loc_list[i-1][2] != loc_order[curr_loc_ind - 1]:
            continue
        travel_time = (loc_list[i][0] - loc_list[i-1][0]).total_seconds()/3600

        dist_const = 1
        if loc_list[i][2] == "CAE":
            dist_const = 0.14
            segment_lookup["College Ave"].append( dist_const/travel_time)
        if loc_list[i][2] == "BSE":
            dist_const = 0.15
            segment_lookup["Bus Stop"].append( dist_const/travel_time)
        if loc_list[i][2] == "SHE":
            dist_const = 0.44
            segment_lookup["Shattuck"].append( dist_const/travel_time)
    print(segment_lookup)
    for key, list in segment_lookup.items():
        # print(np.array(list))
        if list:
            print(key + ": " + str(np.average(np.array(list))))
        else:
            print(key + ": No data")
    return segment_lookup


video_dir = sys.argv[1]
vid_path = Path(video_dir)
# out_path = vid_path/Path("out")
# if os.path.exists(out_path):
#     shutil.rmtree(out_path)
# os.makedirs(out_path)

video_lookup_table = extract_gps_data_in_folders(vid_path)

endpoint_lookup = {"CAS": [], "CAE": [], "BSS": [], "BSE": [], "SHS": [], "SHE": []}

for filename in os.listdir(video_dir):
    # look up specfic longitude values from lookup table and record their timestamp
    curr_dict = video_lookup_table[filename]
    # print(curr_dict["converted_long"])
    for index, long in enumerate(curr_dict["converted_long"]):
        detected_str = assign_endpoint_str(float(long), float(curr_dict["converted_lat"][index]))
        if(detected_str):
            # We are storing a three-part tuple - timestamp, filename, and the associated location string (CAS/CAE/etc) - need the third string when we merge together lists
            if not endpoint_lookup[detected_str]:
                endpoint_lookup[detected_str].append(( datetime.strptime(curr_dict["datetime"][index], "%Y-%m-%d %H:%M:%S"), filename, detected_str))
            elif endpoint_lookup[detected_str][-1][1] != filename:
                endpoint_lookup[detected_str].append(( datetime.strptime(curr_dict["datetime"][index], "%Y-%m-%d %H:%M:%S"), filename, detected_str) )

# Merge the 6 lists together and sort by timestamp
zipped_list = (endpoint_lookup["CAS"] + endpoint_lookup["CAE"] + endpoint_lookup["BSS"] + endpoint_lookup["BSE"] + endpoint_lookup["SHS"] + endpoint_lookup["SHE"])
zipped_list = sorted(zipped_list, key=cmp_to_key(comp_tuples))

# Loop through the list (now ordered by timestamp), and if we see two consecutive 'endpoints' (such as CAE/CAS or BSA/BSE), calculate the average speed for the segment
# This method prints out and returns a dictionary of each segment and the calculated speed - can be further modified to include timestamps, or averaged to see average
# speed for each segment, divided depending on vehicle detection, etc.
calculate_avg_spd(zipped_list)