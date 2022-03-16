from pathlib import Path
import os, sys, shutil
import subprocess
import pandas as pd
import string

if len(sys.argv) != 2:
    print("Usage: ./extract_gps.py <video dir>")
    sys.exit()

def convert_latlong(in_str):
    split_latlong = in_str.split(' ')
    return float(split_latlong[0]) + float(split_latlong[2][:-1])/60.0 + float(split_latlong[3][:-1])/3600.00

def on_bancroft(latitude, longitude):
    # Southwest corner of bancroft -- Intersection of Bancroft and oxford st.
    # lat_0 = 37.867745120011236
    # long_0 = 122.265914980762
    lat_0 = 37.86792981681717
    long_0 = 122.26526052183016
    # Northeast corner of bancroft -- Intersection of Bancroft and Piedmont Ave
    # lat_1 = 37.86974393324088
    # long_1 = 122.25221425754695
    lat_1 = 37.86956443944309
    long_1 = 122.25276142821582
    # Bounding box calculation
    return (latitude > lat_0 and latitude <  lat_1) and (longitude > long_1 and longitude < long_0)

vid_dir = sys.argv[1]
vid_path = Path(vid_dir)
out_path = vid_path/Path("out")
if os.path.exists(out_path):
    shutil.rmtree(out_path)
os.makedirs(out_path)

for filename in os.listdir(vid_path):
    if not filename.endswith(".MP4") and not filename.endswith(".mp4"):
        continue
    # outfile = open(out_path/Path(filename[:-4]+"out.txt"), 'w')
    out_process = subprocess.run(args = ["./exiftool.exe",  "-a", "\"-gps*\"",  "-ee", str(vid_path) + "/" + filename], universal_newlines = True, stdout = subprocess.PIPE)
    output = out_process.stdout
    output_lines = output[output.index("Sample Time"):].split('\n')

    #gps_df = pd.dataframe({'Lat': [], 'Long': [], 'Speed':  })
    lats = []
    longs = []
    speeds = []
    stimes = []
    sdurations = []
    datetimes = []
    vid_on_bancroft = False
    banc_ratio = 0.0
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
            # Can check the most recent latitude and longitude to see if the vid is on bancroft
            # Perform the check here since longitude measurement always comes after latitude measurement
            if on_bancroft(convert_latlong(lats[-1]), convert_latlong(longs[-1])):
                # print(convert_latlong(lats[-1]))
                # print(convert_latlong(longs[-1]))
                vid_on_bancroft = True
                banc_ratio += 1.0
        if line.startswith('GPS Speed'):
            speeds.append(split_line[1])
        if line.startswith('GPS Date/Time'):
            datetimes.append(line[line.index(': ')+2:])
    gps_df = pd.DataFrame( {'lat': pd.Series(lats), 
                            'long': pd.Series(longs), 
                            'speed': pd.Series(speeds),
                            'datetime': pd.Series(datetimes),
                            'sample_time': pd.Series(stimes),
                            'sample_dur': pd.Series(sdurations)
                            } ).set_index('sample_time')

    # Since this is in the Berkeley area, N and W are implied for the latitude and longitude, respectively
    gps_df['converted_lat'] = gps_df['lat'].apply(convert_latlong)
    gps_df['converted_long'] = gps_df['long'].apply(convert_latlong)

    #print(gps_df[['converted_lat', 'converted_long', 'speed', 'datetime']].head())
    print(filename + " on Bancroft Way: " + str(vid_on_bancroft), end="\t")
    print(filename + " Bancroft Ratio: " + str(banc_ratio/59))
    #print(gps_df.head())
    #print(output_lines[:10])
    # outfile.close()
