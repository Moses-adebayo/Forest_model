#!/bin/bash -l
#SBATCH -A CLI185
#SBATCH -N 1
#SBATCH -J Site_1
#SBATCH --mail-user=moses_adebayo@mines.edu
#SBATCH --mail-type=ALL
#SBATCH -t 00:45:00
#SBATCH -p batch
srun -n 50 ats --xml_file=../Site2_param1.xml &> out.log
python post_run.py

