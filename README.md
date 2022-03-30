# curb-monitor
Curb monitoring system. A prototype.

# 1. Setup Envionment

1. Create a new conda environment and activate it
    ```
    conda create --name curb
    conda activate curb
    conda install pip
    ```
2. Install requirement packages
    ```
    pip install -r requirements.txt
    ```
    You might want to install the cuda version of pytorch again using the cmd [here](https://pytorch.org/get-started/locally/) if you want to use gpu for pytorch

# 2. Object Detection Overall Flow

1. Copy image data from s3 to savio
    1. login to savio data transfer node
        ```
        ssh yourusername@dtn.brc.berkeley.edu
        ```
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
        rclone copy -P s3_frank:curbside-data/all_videos_1 /global/scratch/users/sidali/all_videos_1
        ```
    1. delete the corrupted video(remove video smaller than 140M)
        ```
        cd /global/scratch/users/sidali/all_videos_1
        find . -name "*.mp4" -type 'f' -size -139M -delete
        ```
    1. Split data into subfolders
        ```
        dir_size=1500
        dir_name="video"
        n=$((`find . -maxdepth 1 -type f | wc -l`/$dir_size+1))
        for i in `seq 1 $n`; do mkdir -p "$dir_name$i"; find . -type f -maxdepth 1 | head -n $dir_size | xargs -i mv "{}" "$dir_name$i"; done
        ```