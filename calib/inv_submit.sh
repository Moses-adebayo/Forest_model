#!/bin/bash -l
#SBATCH -A CLI185
#SBATCH -N 1
#SBATCH -J test
#SBATCH --mail-user=moses_adebayo@mines.edu
#SBATCH --mail-type=ALL
#SBATCH -t 00:50:00
#SBATCH -p batch
python pre_write.py
python $ATS_SRC_DIR/tools/input_converters/xml-1.5-master.py -o Site_1_profile_convert.xml Site_1_profile.xml
srun -n 50 ats --xml_file=Site_1_profile_convert.xml &> out.log
python post_run.py
