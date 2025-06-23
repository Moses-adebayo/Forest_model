import numpy as np
import pandas as pd
import subprocess
import re
import h5py
from scipy.optimize import curve_fit
import os
import time
from write_script import write_script

param=np.loadtxt('params.txt') 
with open('all_param.txt', 'a') as f:
    f.write(f'Iteration new: {param}\n')
write_script(0,param[0],param[1],param[2],param[3])
