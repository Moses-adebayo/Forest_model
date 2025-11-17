#!/bin/bash -l
#SBATCH -A CLI185
#SBATCH -N 1
#SBATCH -J run_ensemble
#SBATCH --mail-user=moses_adebayo@mines.edu
#SBATCH --mail-type=ALL
#SBATCH -t 00:35:00
#SBATCH -p batch

srun -n 50 ats --xml_file=../Site_1_Step1.xml&> out.log
