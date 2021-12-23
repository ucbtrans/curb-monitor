## Change List
1. config [rclone](https://rclone.org/s3/) 
    ```
    module load rclone
    rclone config
    ```

1. download s3 data to savio using [rclone](https://rclone.org/s3/) 
    ```
    rclone copy your_s3_config_name:curbside-data/vid_folder_123 /global/scratch/users/your_savio_username/vid_folder_123
    ```

    for example
    ```
     rclone copy s3_frank:curbside-data/bus_dashcam_videos /global/scratch/users/sidali/bus_dashcam_videos
    ```
1. update the data folder path under curb-monitor/savio_jobs/video_detect/production_job_gpu.sh

1. go to curb-monitor/scripts/executables and clone the exiftool tool:
    ```
    cd scripts/executables
    git clone https://github.com/exiftool/exiftool.git
    ```
