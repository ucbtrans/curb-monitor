from pathlib import Path
import os, sys, shutil
import subprocess
import pandas as pd
import string
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

if len(sys.argv) != 2:
    print("Usage: ./convert_label_csv.py <label csv>")
    sys.exit()

label_csv = Path(sys.argv[1])
label_df = pd.read_csv(label_csv, names=['label', 'left', 'top', 'width', 'height', 'filename', 'img_width', 'img_height'], header=None)
labels = ['car', 'bus', 'other_truck', 'uhaul_truck', 'fedex_truck', 'ups_truck', 'amazon_truck']
label_mapping = dict(zip(labels, [*range(len(labels))]))

for name, group in label_df.groupby('filename'):
    json_obj = \
        {   
            'file': name, 
            'image_size': [{'width': group['img_width'].iloc[0], 'height': group['img_height'].iloc[0],'depth': 3}],
            'annotations': [],
            'categories': []
        }
    for index, row in group.iterrows():
        json_obj['annotations'].append(
            {
                'class_id': label_mapping[row['label']],
                'left': row['left'],
                'top': row['top'],
                'width': row['width'],
                'height': row['height']
            })
    for key, val in label_mapping.items():
        json_obj['categories'].append(
            {
                'class_id': val,
                'name': key
            })
    filename = name.split('.')[0] + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4, cls=NpEncoder)