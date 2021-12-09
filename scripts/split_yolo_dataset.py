import random
import pathlib
import os
from re import X
from shutil import copyfile
import argparse
import glob
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0] 

#

def copy_files(files, input_images_path, input_labels_path, output_images_path, output_label_path):
    for image_name in files:
        val_name = os.path.splitext(image_name)[0] + '.txt'
        output_image_file_path = os.path.join(output_images_path, image_name)
        input_image_file_path = os.path.join(input_images_path, image_name)
        output_label_file_path = os.path.join(output_label_path, val_name)
        input_label_file_path = os.path.join(input_labels_path, val_name)
        copyfile(input_image_file_path, output_image_file_path)
        copyfile(input_label_file_path, output_label_file_path)


def run(input_dir=ROOT / 'data/images', output_dir=ROOT / 'output'):
    print(output_dir)
    output_trains_images = output_dir / 'trains/images'
    output_valids_images = output_dir / 'valids/images'
    output_trains_labels = output_dir / 'trains/labels'
    output_valids_labels = output_dir / 'valids/labels'
    # make dir first
    print(output_trains_images)
    pathlib.Path(output_trains_images).mkdir(parents=True, exist_ok=True) 
    pathlib.Path(output_valids_images).mkdir(parents=True, exist_ok=True)
    pathlib.Path(output_trains_labels).mkdir(parents=True, exist_ok=True) 
    pathlib.Path(output_valids_labels).mkdir(parents=True, exist_ok=True)

    images_path = Path(input_dir).resolve()
    labels_path = images_path.parents[0] / 'labels'

    images_names = os.listdir(str(images_path))
    random.shuffle(images_names)
    train_len = int(len(images_names) * 0.8)
    train_images = images_names[:train_len]
    val_images = images_names[train_len:]

    copy_files(train_images, images_path, labels_path, output_trains_images, output_trains_labels)
    copy_files(val_images, images_path, labels_path, output_valids_images, output_valids_labels)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=str, default=ROOT / 'data/images', help='yolo images folder')
    parser.add_argument('--output-dir', type=str, default=ROOT / 'output', help='output dir')
    opt = parser.parse_args()
    print(opt)
    return opt


def main():
    opt = parse_opt()
    run(**vars(opt))


if __name__ == "__main__":
    main()
