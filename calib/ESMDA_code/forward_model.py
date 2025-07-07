import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")
import time
import pandas as pd
import shutil
import subprocess
import copy

def run_model(s,Num_ens):
    s=10**s
    for i in range(Num_ens):
        np.savetxt('param'+str(i+1)+'.txt',s[i,:]
    with open("matlab_signal.txt", "w") as f:
        f.write("done")
    with open("matlab_forward.txt", "w") as f:
        f.write("wait")
    subprocess.run(['git','add','param*'])
    subprocess.run(['git','add','matlab*'])
    subprocess.run(['git','commit','-m',"generated ensemble"])
    subprocess.run(['git','push','origin','ESMDA'])
    time.sleep(120)
    check_forward_signal()
    sim_obs=np.loadtxt("forward_obs.txt")
    return sim_obs
def check_forward_signal(filename="matlab_forward.txt"):
    """
    Waits until the specified file contains the word "done".
    
    Parameters:
    - filename: The name of the file that MATLAB updates.
    
    The function polls the file every second. Once the file contains "done",
    the function returns and the rest of the Python script can continue.
    """
    while True:
        subprocess.run(['git','pull','origin','ESMDA'])
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read().strip()  # Remove any extra whitespace/newlines
                if content.lower() == "done":
                    #print("Python: Detected 'done'. Resuming execution.")
                    break
        time.sleep(120)