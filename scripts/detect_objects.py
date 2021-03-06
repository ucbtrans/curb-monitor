#!/usr/bin/env python3

"""
Script for extracting training raw images from bus dashcam recording
Usage:
    $ python .\scripts\detect_objects.py --save-csv --class 1 3 4 5 6  --conf-thres 0.6 --img 640 --debug --weights .\models\curb_prod_model\weights\best.pt --source ..\capstone\
"""


import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn

from get_gps_metadata import extract_gps_data_in_folders, find_nearest_frame_from_folder

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory

from yolov5.models.experimental import attempt_load
from yolov5.utils.datasets import LoadImages, LoadStreams
from yolov5.utils.general import apply_classifier, check_img_size, check_imshow, check_requirements, check_suffix, colorstr, \
    increment_path, non_max_suppression, print_args, save_one_box, scale_coords, set_logging, \
    strip_optimizer, xyxy2xywh, yolov5_in_syspath
from yolov5.utils.plots import Annotator, colors
from yolov5.utils.torch_utils import load_classifier, select_device, time_sync
import csv

@torch.no_grad()
def run(weights='yolov5s.pt',  # model.pt path(s)
        source=ROOT / 'data/images',  # file/dir/URL/glob
        imgsz=640,  # inference size (pixels)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_csv=True,  # save results to *.csv
        debug=False,  # save detected images/videos for bug
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        project='runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        save_orginal_image=False # Save original picture
        ):
    source = str(source)
    folder_gps_dict = extract_gps_data_in_folders(source)

    save_debug_img =  debug and not source.endswith('.txt')  # save inference images

    if isinstance(imgsz, int):
        imgsz = [imgsz, imgsz]
    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=False)  # increment run
    (save_dir / 'csv' if save_csv else save_dir).mkdir(parents=True, exist_ok=True)  # make dir
    (save_dir / 'images' if save_orginal_image else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(device)

    # Load model
    w = str(weights[0] if isinstance(weights, list) else weights)
    classify, suffixes = False, ['.pt']
    check_suffix(w, suffixes)  # check weights have acceptable suffix
    stride, names = 64, [f'class{i}' for i in range(1000)]  # assign defaults
    with yolov5_in_syspath():
        model = torch.jit.load(w) if 'torchscript' in w else attempt_load(weights, map_location=device)
        stride = int(model.stride.max())  # model stride
        names = model.module.names if hasattr(model, 'module') else model.names  # get class names
        if classify:  # second-stage classifier
            modelc = load_classifier(name='resnet50', n=2)  # initialize
            modelc.load_state_dict(torch.load('resnet50.pt', map_location=device)['model']).to(device).eval()
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=True)
    bs = 1  # batch_size
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, *imgsz).to(device).type_as(next(model.parameters())))  # run once
    dt, seen = [0.0, 0.0, 0.0], 0

    csv_writer = ...
    if save_csv:
        csv_path = str(save_dir / 'csv' / 'detected.csv')  # detected.csv

        csv_header = ['time', 'latitude', 'longitude', 'speed', 'original_file', 'image_file', 'obj_class_name', 'obj_class',  'x', 'y', 'w', 'h', 'confidences']

        # open the file in the write mode
        csv_f = open(csv_path, 'w', encoding='UTF8', newline='')

        # create the csv writer
        csv_writer = csv.writer(csv_f)

        # write a row to the csv file
        csv_writer.writerow(csv_header)

    for path, img, im0s, vid_cap in dataset:
        t1 = time_sync()
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        visualize = False #increment_path(save_dir / Path(path).stem, mkdir=True)
        pred = model(img, augment=False, visualize=visualize)[0]
        t3 = time_sync()
        dt[1] += t3 - t2

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic = False, max_det=max_det)
        dt[2] += time_sync() - t3

        # Second-stage classifier (optional)
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            seen += 1
            p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path

            save_path = str(save_dir / p.name)  # img.jpg
            save_original_name = p.stem + ('' if dataset.mode == 'image' else f'_{frame}') + '.jpg'
            save_original_path = str(save_dir / 'images') + save_original_name  # f_frame.jpg
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            annotator = Annotator(im0, line_width=3, example=str(names))
            ## for extract original image 
            original_img = im0.copy()
            should_save_org_img = False
            
            if len(det):
                should_save_org_img = True
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_csv:  # Write to file
                        try:
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            #csv_header = ['time', 'latitude', 'longitude', 'speed', 'original_file', 'image_file', 'obj_class_name', 'obj_class',  'x', 'y', 'w', 'h', 'confidences']
                            # create the csv writer
                            frame_info = find_nearest_frame_from_folder( folder_gps_dict, p.name, frame)
                            csv_row = [frame_info['datetime'], frame_info['converted_lat'], frame_info['converted_long'], frame_info['speed'], p.name, save_original_name, names[int(cls)], int(cls), xywh[0], xywh[1], xywh[2], xywh[3], conf.item()]
                            csv_writer.writerow(csv_row)
                        except:
                            print("Failed to get frame info" + p.name + " " +frame)

                    if save_debug_img or view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = f'{names[c]} {conf:.2f}'
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # Print time (inference-only)
            print(f'{s}Done. ({t3 - t2:.3f}s)')

            # Stream results
            im0 = annotator.result()
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            if save_orginal_image and should_save_org_img:
                cv2.imwrite(save_original_path, original_img)

            # Save results (image with detections)
            if save_debug_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:  # 'video' or 'stream'
                    if vid_path[i] != save_path:  # new video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)
    # close the file
    csv_f.close()

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    print(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_csv or save_debug_img:
        s = f"\n{len(list(save_dir.glob('csv/*.csv')))} csv saved to {save_dir / 'csv'}" if save_csv else ''
        print(f"Results saved to {colorstr('bold', save_dir)}{s}")


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov5s.pt', help='model path(s)')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-csv', action='store_true', help='save results to *.txt')
    parser.add_argument('--debug', action='store_true', help='save debug image/video')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--save-orginal-image', default=False, help='Save original picture')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(FILE.stem, opt)
    return opt


def main():
    opt = parse_opt()
    #check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    main()
