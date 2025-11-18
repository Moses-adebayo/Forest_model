import numpy as np
import os
import subprocess
import time
from scipy.io import savemat, loadmat
from scipy.stats import qmc
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from ES_MDA import ES_MDA
import pandas as pd
import utility
#import forward_model
import sobol_seq
import copy
def submit():
    while True:
        subprocess.run(['git', 'pull', 'origin', 'ES_MDA2'])
        with open('Site1_param_ats_prompt.txt', 'r') as f:
            content = f.read().strip()   
        if 'done' in content:
            # copy final ats files
            os.chdir('data/')
            subprocess.run(['sbatch', 'run_ensemble.sh'])
            subprocess.run(['sbatch', 'run_ensemble2.sh'])
            subprocess.run(['sbatch', 'run_ensemble3.sh'])
            os.chdir('../')
            print('all scripts submitted.....proceed')
            break
        else:
            # Wait for 600 seconds
            time.sleep(600)
while True:
    submit()
    while True:
        exist=all(os.path.exists(f'Site1_param{i}/checkpoint_final.h5') for i in range(1, 11))
        if exist:
            print('all checkpoints found.....proceed')
            subprocess.run(['git', 'pull', 'origin', 'ES_MDA2'])
            with open('Site1_param_ats_prompt.txt', 'w') as f:
                f.write('wait')
            subprocess.run(['git', 'add', 'Site1_param_ats_prompt.txt'])
            subprocess.run(["git", "commit", "-m", "inversion in progress"])
            subprocess.run(['git', 'push', 'origin', 'ES_MDA2'])
            break
        else:
            time.sleep(600)
    for i in range(1, 11):
        os.remove(f'Site1_param{i}/checkpoint_final.h5')