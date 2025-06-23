import numpy as np
import pandas as pd
import subprocess
import re
import h5py
from scipy.optimize import curve_fit
import os
import time
from write_script import write_script
import zipfile
import time
def wait_for_matlab_signal(filename="matlab_signal.txt"):
    """
    Waits until the specified file contains the word "done".
    
    Parameters:
    - filename: The name of the file that MATLAB updates.
    
    The function polls the file every second. Once the file contains "done",
    the function returns and the rest of the Python script can continue.
    """
    while True:
        subprocess.run(['git','pull','origin','short_model'])
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read().strip()  # Remove any extra whitespace/newlines
                if content.lower() == "done":
                    #print("Python: Detected 'done'. Resuming execution.")
                    break
        time.sleep(120)
def check_matlab_signal(filename="matlab_exe.txt"):
    """
    Waits until the specified file contains the word "done".
    
    Parameters:
    - filename: The name of the file that MATLAB updates.
    
    The function polls the file every second. Once the file contains "done",
    the function returns and the rest of the Python script can continue.
    """
    while True:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read().strip()  # Remove any extra whitespace/newlines
                if content.lower() == "done":
                    #print("Python: Detected 'done'. Resuming execution.")
                    break
        time.sleep(120)
		
for i in range(1,101):
    wait_for_matlab_signal()
    with open("matlab_exe.txt", "w") as f:
        f.write("wait")
    #subprocess.run(['git','pull','origin','short_model'])
    subprocess.run(['git','add','matlab_exe.txt'])
    subprocess.run(['git','commit','-m',"inversion running"])
    subprocess.run(['git','push','origin','short_model'])
    subprocess.run(['sbatch','inv_submit.sh'])
    check_matlab_signal()
    subprocess.run(['git','add','data_set_edit_short.zip'])
    subprocess.run(['git','add','matlab_exe.txt'])
    subprocess.run(['git','add','matlab_signal.txt'])
    subprocess.run(['git','commit','-m',"inversion running"])
    subprocess.run(['git','push','origin','short_model'])
    time.sleep(400)
