#!/bin/bash
# Job name:
#SBATCH --job-name=pre-video-process-job
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
#SBATCH --time=12:00:00
#
## Command(s) to run (example):

#readme
#please define the following variable
export VIDEOS_ABS_PATH=path_to_data_folder

module load python gcc opencv cmake
pip install --user --upgrade pip setuptools wheel && pip install --user -r ~/curb-monitor/requirements.txt

# run job
cd ~/curb-monitor && python ./scripts/extract_training_raw_pictures.py --class 3 4 --conf-thres 0.6 --img 640 --sample-interval 24  --nosave --weights ./models/pre_process_model/weights/best.pt --source $VIDEOS_ABS_PATH