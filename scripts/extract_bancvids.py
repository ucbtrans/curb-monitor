from pathlib import Path
import os, sys, shutil
import subprocess
import pandas as pd
import string

if len(sys.argv) != 3:
    print("Usage: ./extract_bancvids.py <video dir> <file of valid vid filenames>")
    sys.exit()

vid_dir = sys.argv[1]
vid_path = Path(vid_dir)
banc_path = vid_path/Path("bancroft_vids")
curr_path = Path(".")
if os.path.exists(banc_path):
    shutil.rmtree(banc_path)
os.makedirs(banc_path)

vid_file = open(sys.argv[2], 'r')

for line in vid_file:
    fname = line.split()[0]
    #print(fname)
    shutil.move(vid_path/fname, banc_path/fname)