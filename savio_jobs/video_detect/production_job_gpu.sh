#!/bin/bash
# Job name:
#SBATCH --job-name=video-detect-job
#
# Account:
#SBATCH --account=fc_control
#
# Partition:
#SBATCH --partition=savio3_gpu
#
# Number of nodes:
#SBATCH --nodes=1
#
# Number of tasks (one for each GPU desired for use case) (example):
#SBATCH --ntasks=1
#
# Processors per task (please always specify the total number of processors twice the number of GPUs):
#SBATCH --cpus-per-task=4
#
#Number of GPUs, this can be in the format of "gpu:[1-4]", or "gpu:K80:[1-4] with the type included
#SBATCH --gres=gpu:GTX2080TI:1
#
# Wall clock limit:
#SBATCH --time=72:00:00
#
## Command(s) to run (example):

#readme
#please define the following variable
export VIDEOS_ABS_PATH=path_to_data_folder #/global/scratch/users/sidali/bus_vids_10_20_21
export OUT_PUT_PATH=path_to_output_folder #/global/scratch/users/sidali/runs/detect

module load python gcc opencv cmake
pip install --user --upgrade pip setuptools wheel && pip install --user -r ~/curb-monitor/requirements.txt

# run job
cd ~/curb-monitor && python ./scripts/detect_objects.py --project $OUT_PUT_PATH --save-csv --class 1 3 4 5 6 --conf-thres 0.25 --img 640  --weights ./models/curb_prod_model/weights/best.pt --source $VIDEOS_ABS_PATH
