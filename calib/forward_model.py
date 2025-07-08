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
	s_tempp=copy.deepcopy(s)
	# set upper bound for all parameters
	para_u = np.array([-9, -9, -3, -0.2, -3, -0.2, 5, 3.5])
	# set lower bound for all parameters
	para_l = np.array([-17, -17, -6.5, -1.2, -6.5, -1.2, 0.5, 2.59])
    # transform s to original values
    s_tempp[:, 0] = para_l[0] + (para_u[0]-para_l[0]) * (np.exp(s[:, 0]) / (1 + np.exp(s[:, 0])))
    s_tempp[:, 1] = para_l[1] + (para_u[1]-para_l[1]) * (np.exp(s[:, 1]) / (1 + np.exp(s[:, 1])))
    s_tempp[:, 2] = para_l[2] + (para_u[2]-para_l[2]) * (np.exp(s[:, 2]) / (1 + np.exp(s[:, 2])))
    s_tempp[:, 3] = para_l[3] + (para_u[3]-para_l[3]) * (np.exp(s[:, 3]) / (1 + np.exp(s[:, 3])))
    s_tempp[:, 4] = para_l[4] + (para_u[4]-para_l[4]) * (np.exp(s[:, 4]) / (1 + np.exp(s[:, 4])))
    s_tempp[:, 5] = para_l[5] + (para_u[5]-para_l[5]) * (np.exp(s[:, 5]) / (1 + np.exp(s[:, 5])))
	s_tempp[:, 6] = para_l[6] + (para_u[6]-para_l[6]) * (np.exp(s[:, 6]) / (1 + np.exp(s[:, 6])))
	s_tempp[:, 7] = para_l[7] + (para_u[7]-para_l[7]) * (np.exp(s[:, 7]) / (1 + np.exp(s[:, 7])))
    s_tempp=10**s_tempp
    for i in range(Num_ens):
        np.savetxt('param'+str(i+1)+'.txt',s_tempp[i,:]
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