# savio documentations

https://docs-research-it.berkeley.edu/services/high-performance-computing/user-guide/

# How to run a savio jobs
1. ssh to the savio cluster
    ```
    ssh your_user_name@hpc.brc.berkeley.edu
    ```
2. clone this git repo to the your savio home folder
    ```
    git clone https://github.com/ucbtrans/curb-monitor.git
    cd curb-monitor
    ```
3. read each jobs readme and change the config you might need to change, for example, dataset location under training\curb\curb.yaml
    ```
    module load nano
    nano ./training/curb/curb.yaml
    ```

4. run the training job
    ```
    sbatch ./savio_jobs/curb/production_job_gpu.sh
    ```
5. check your job
    ```
    sq
    ```
6. cancel your job 
    ```
    scancel <jobid>
    ```