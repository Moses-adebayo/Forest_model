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
from write_script import write_script_site1 as write_script
import modvis.ats_xdmf as xdmf
import modvis.plot_vis_file as pv
def forward(Num_ens):
    data=[]
    for i in range(Num_ens):
        visfile = xdmf.VisFile('Site1_param'+str(i+1), domain=None, load_mesh=True, columnar=True, ats_version=1.6)
        ihead = pv.plot_column_head(visfile, col_ind = 196)
        
        data.append(ihead.values.ravel()-242.62426)
    return np.vstack(data)
# initialization
Num_ens=10
Dim_est=5
Na=10
Alpha=1/np.array([0.07,0.075,0.08,0.09,0.095,0.10,0.105,0.12,0.13,0.135])
#ncores=10

#load observation data
obs=np.loadtxt('data/Site1_WL_obs.txt')

var_obs = np.ones_like(obs)
obs=np.array([obs])
obs=obs.T

# set the error for different kinds of measurements
var_obs[:]=0.5 # SP
#var_obs[110:]=1 # SP
R=np.diag(var_obs)

s=np.zeros((Num_ens,Dim_est,Na+1))
data = sobol_seq.i4_sobol_generate(dim_num= Dim_est, n = Num_ens)
# set upper bound for all parameters
para_u=np.array([-10,-10,-3,0.4,-0.48])# bedrock permeability, top soil permeability, Qv
# set lower bound for all parameters
para_l=np.array([-15,-15,-7,0.05,-2])
sampler = qmc.Sobol(d=Dim_est, scramble=True, seed=8)
raw = sampler.random_base2(m=5)[:Num_ens]  # shape (9, 10)
data1 = qmc.scale(raw, l_bounds=para_l,u_bounds=para_u)
s_temp = copy.deepcopy(data1)
s_temp[:, 0] = np.log((data1[:, 0] - para_l[0]) / (para_u[0] - data1[:, 0]))
s_temp[:, 1] = np.log((data1[:, 1] - para_l[1]) / (para_u[1] - data1[:, 1]))
s_temp[:, 2] = np.log((data1[:, 2] - para_l[2]) / (para_u[2] - data1[:, 2]))
s_temp[:, 3] = np.log((data1[:, 3] - para_l[3]) / (para_u[3] - data1[:, 3]))
s_temp[:, 4] = np.log((data1[:, 4] - para_l[4]) / (para_u[4] - data1[:, 4]))
#s_temp=loadmat('../../s_tem3.mat')['s_tem'] #useful for restarting the inversion if it crashed for some reasons, else comment out
s[:,:,0]=s_temp

savemat('./s_tem0.mat', {'s_tem':s[:,:,0]}) # save s for each step
write=10**(data1.copy())
for i in range (Num_ens):
    write_script(write[i][0],write[i][1],write[i][2],write[i][3],write[i][4],i+1)
    np.savetxt('Site1_param'+str(i+1)+'.txt',write[i])
os.chdir('data/')
subprocess.run(['sbatch', 'run_ensemble.sh'])
subprocess.run(['sbatch', 'run_ensemble2.sh'])
subprocess.run(['sbatch', 'run_ensemble3.sh'])
os.chdir('../')
while True:
    exist=all(os.path.exists(f'param{i}/checkpoint_final.h5') for i in range(1, 11))
    if exist:
        print('all checkpoints found.....proceed')
        break
    else:
        time.sleep(600)
for i in range(1, 11):
    os.remove(f'Site1_param{i}/checkpoint_final.h5')
for t in range(len(Alpha)):
    sim_obs= forward(Num_ens)# shape of sim_obs (Num_ens,Num_obs)# combine from param1 to param10
    np.savetxt('./sim_obs' + str(t) + '.txt', np.mean(sim_obs,axis=0))
    
    rmse=np.sqrt(np.mean((np.mean(sim_obs,axis=0)-obs.flatten())**2))
    print('RMSE ite_', t, ' : ', rmse) # not the exact RMSE definition
    
    nse = np.zeros(Num_ens)
    for i in range(Num_ens):
        nse[i] = utility.calculate_nse(obs.reshape(-1), sim_obs[i, :].T)
    nse_mean = np.mean(nse, 0)
    print('NSE ite_', t, ' : ', nse_mean)
    
    # 写入 metrics.txt 文件（追加模式）
    with open('metrics.txt', 'a') as f:
        f.write(f'Iteration {t}:\n')
        f.write(f'  RMSE: {rmse:.6f}\n')
        f.write(f'  NSE : {nse_mean:.6f}\n')
        f.write('\n')
    
    s[:,:,t+1] = ES_MDA(Num_ens, s[:,:,t], obs, sim_obs, Alpha[t], R, [], 2)
    s_tem=s[:,:,t+1]
    savemat('./s_tem' + str(t+1) + '.mat', {'s_tem':s_tem}) # save s for each step
    savemat('./sim_obs' + str(t) + '.mat', {'sim_obs':sim_obs}) # save observation for each step
    
    s_tempp=copy.deepcopy(s_tem)
    s_tempp[:, 0] = para_l[0] + (para_u[0]-para_l[0]) * (np.exp(s_tem[:, 0]) / (1 + np.exp(s_tem[:, 0])))
    s_tempp[:, 1] = para_l[1] + (para_u[1]-para_l[1]) * (np.exp(s_tem[:, 1]) / (1 + np.exp(s_tem[:, 1])))
    s_tempp[:, 2] = para_l[2] + (para_u[2]-para_l[2]) * (np.exp(s_tem[:, 2]) / (1 + np.exp(s_tem[:, 2])))
    s_tempp[:, 3] = para_l[3] + (para_u[3]-para_l[3]) * (np.exp(s_tem[:, 3]) / (1 + np.exp(s_tem[:, 3])))
    s_tempp[:, 4] = para_l[4] + (para_u[4]-para_l[4]) * (np.exp(s_tem[:, 4]) / (1 + np.exp(s_tem[:, 4])))
    write=10**(s_tempp)
    
    for i in range (Num_ens):
        write_script(write[i][0],write[i][1],write[i][2],write[i][3],write[i][4],i+1)
        np.savetxt('Site1_param'+str(i+1)+'.txt',write[i])
    os.chdir('data/')
    subprocess.run(['sbatch', 'run_ensemble.sh'])
    subprocess.run(['sbatch', 'run_ensemble2.sh'])
    subprocess.run(['sbatch', 'run_ensemble3.sh'])
    os.chdir('../')
    while True:
        exist=all(os.path.exists(f'Site1_param{i}/checkpoint_final.h5') for i in range(1, 11))
        if exist:
            print('all checkpoints found.....proceed')
            break
        else:
            time.sleep(600)
    for i in range (1,11):
        os.remove(f'Site1_param{i}/checkpoint_final.h5')
    print('end of iteration '+str(t+1))
t =len(Alpha)+1
sim_obs= forward(Num_ens)# shape of sim_obs (Num_ens,Num_obs)# combine from param1 to param10
np.savetxt('./sim_obs' + str(t) + '.txt', np.mean(sim_obs,axis=0))
savemat('./sim_obs' + str(t) + '.mat', {'sim_obs':sim_obs}) # save observations for each step