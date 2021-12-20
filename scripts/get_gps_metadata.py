#### FOR THE SCRIPTS/HELPER FUNCTIONS TO WORK, THE exiftool.exe FILE MUST BE IN THE SAME LEVEL DIRECTORY AS THIS SCRIPT                                         ####
#### exiftool.exe MUST ALSO BE EXECUTABLE - IF THERE IS A PERMISSION DENIED ERROR, TRY CHANGING THE PERMISSIONS WITH THIS COMMAND: >chmod +777 exiftool.exe     ####

from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import os, sys, shutil
import subprocess
import string

# Converts latitude and longitude strings into numerical (decimal) versions of 
# lat and long
def convert_latlong(in_str):
    split_latlong = in_str.split(' ')
    return float(split_latlong[0]) + float(split_latlong[2][:-1])/60.0 + \
        float(split_latlong[3][:-1])/3600.00

# Returns the dataframe containing the GPS data as well as the measured fps from
# the metadata
def extract_gps_to_dataframe(filename, fps=30):
    if not filename.endswith(".MP4") and not filename.endswith(".mp4"):
        print("Error: Filename doesn't end with .MP4/.mp4")
        exit(1)
    out_process = subprocess.run(args = ["./exiftool.exe",  "-a", "\"-gps*\"", \
         "-ee", filename], universal_newlines = True, stdout = subprocess.PIPE)
    output = out_process.stdout
    output_lines = output[output.index("Sample Time"):].split('\n')

    creation_date = output[output.index("Create Date"):].split('\n')[0]\
        .split(':')
    frame_rate_line = int(np.round(float(output[output\
        .index("Video Frame Rate"):].split('\n')[0].split(':')[1])))
    creation_date = (":".join(creation_date[1:])).strip()
    creation_date = datetime.strptime(creation_date, '%Y:%m:%d %H:%M:%S')
    time_delta = timedelta(seconds=1)
    fps = frame_rate_line


    lats = []
    longs = []
    speeds = []
    stimes = []
    sdurations = []
    datetimes = []
    for line in output_lines:
        if len(line) == 0:
            continue
        split_line = line.split(':')
        split_line[1] = split_line[1][1:]
        if line.startswith('Sample Time'):
            if len(split_line) == 2:
                stimes.append(float(split_line[1][:-2]))
            else:
                stimes.append(float(split_line[3]))
        if line.startswith('Sample Duration'):
            sdurations.append(split_line[1])
        if line.startswith('GPS Latitude'):
            lats.append(split_line[1])
        if line.startswith('GPS Longitude'):
            longs.append(split_line[1])
        if line.startswith('GPS Speed'):
            speeds.append(split_line[1])
        if line.startswith('GPS Date/Time'):
            datetimes.append(creation_date + time_delta * int(stimes[-1]))
    gps_dict = {'lat': lats, 
                'long': longs, 
                'speed': speeds,
                'datetime': datetimes,
                'sample_time': stimes,
                }

    # Since this is in the Berkeley area, N and W are implied for the latitude
    # and longitude, respectively
    gps_dict['converted_lat'] = [convert_latlong(x) for x in gps_dict['lat']]
    gps_dict['converted_long'] = [convert_latlong(x) for x in gps_dict['long']]
    
    return gps_dict, fps

# Given the dataframe of gps locations, the fps, and the frame number, extract
# the gps data 
# Note - this method expects the frames to be 0 indexed, and treats 'seconds' 
# as 0 indexed as well.
# This means that a 60 second video has indices 0 through 59 - if we have 30 
# fps, the bounds of this method's frames range from 0 to 59*30 (or 0 to 1770)
def find_nearest_frame(dict, frame_number, fps):
    index = int(np.round(frame_number/fps, 0))
    extracted_row = {
                    'lat': dict['lat'][index], 
                    'long': dict['long'][index], 
                    'speed': dict['speed'][index],
                    'datetime': dict['datetime'][index],
                    'sample_time': dict['sample_time'][index],
                    'converted_lat': dict['converted_lat'][index],
                    'converted_long': dict['converted_long'][index]
                    }  
    return extracted_row

# Generate a nested data structure to hold all of the video gps data in a folder
# This function returns a nested dictionary where the key is the filename in the 
# folder and the value is the dictionary of gps data for the given file
def extract_gps_data_in_folders(folder_name):
    folder_path = Path(folder_name)
    gps_data_from_folder = {}
    for filename in os.listdir(folder_path):
        gps_data_from_folder[filename], _ = extract_gps_to_dataframe\
            (folder_name + "/" + filename)
    return gps_data_from_folder

# Given a filename, a frame number, and a nested gps dictionary (from the above 
# function), find the associated GPS data for the frame
# Note that the given filename is the filename -within- the folder itself, not
# the full path. An example of this is that if the full path of the file is 
# dash_vids/GRMN4444.MP4, then the provided filename should be "GRMN4444.MP4"
def find_nearest_frame_from_folder(gps_folder_dict, filename, frame_number,\
    fps=30):
    return find_nearest_frame(gps_folder_dict[filename], frame_number, fps)


# Example Test:
# gps_dict, fps = extract_gps_to_dataframe("test_vids/GRMN0142.MP4")
# print(find_nearest_frame(gps_dict, fps, 788))
folder_gps_dict = extract_gps_data_in_folders("test_vids")
print(find_nearest_frame_from_folder( folder_gps_dict, "GRMN0142.MP4", 788))
print(find_nearest_frame_from_folder( folder_gps_dict, "GRMN0143.MP4", 33))