import numpy as np
import os
from scipy.io import savemat, loadmat
import warnings
warnings.filterwarnings("ignore")
from ES_MDA import ES_MDA
import pandas as pd
import utility
import forward_model
import sobol_seq

# initialization
Num_ens=10
Dim_est=8
Na=4
Alpha=np.array([9.333,7.0,4.0,2.0])
#ncores=10

#load observation data
obs=np.loadtxt('observation.txt')

var_obs = np.ones_like(obs)
obs=np.array([obs])
obs=obs.T

# set the error for different kinds of measurements
var_obs[:]=0.5 # discharge
R=np.diag(var_obs)

s=np.zeros((Num_ens,Dim_est,Na+1))
data = sobol_seq.i4_sobol_generate(dim_num= 8, n = 10)
# set upper bound for all parameters
para_u = np.array([-9, -9, -3, -0.2, -3, -0.2, 5, 3.5])
# set lower bound for all parameters
para_l = np.array([-17, -17, -6.5, -1.2, -6.5, -1.2, 0.5, 2.59])
data1 = para_l+data*(para_u-para_l)
s_temp = data1
s_temp[:, 0] = np.log((s_temp[:, 0] - para_l[0]) / (para_u[0] - s_temp[:, 0]))
s_temp[:, 1] = np.log((s_temp[:, 1] - para_l[1]) / (para_u[1] - s_temp[:, 1]))
s_temp[:, 2] = np.log((s_temp[:, 2] - para_l[2]) / (para_u[2] - s_temp[:, 2]))
s_temp[:, 3] = np.log((s_temp[:, 3] - para_l[3]) / (para_u[3] - s_temp[:, 3]))
s_temp[:, 4] = np.log((s_temp[:, 4] - para_l[4]) / (para_u[4] - s_temp[:, 4]))
s_temp[:, 5] = np.log((s_temp[:, 5] - para_l[5]) / (para_u[5] - s_temp[:, 5]))
s_temp[:, 6] = np.log((s_temp[:, 6] - para_l[6]) / (para_u[6] - s_temp[:, 6]))
s_temp[:, 7] = np.log((s_temp[:, 7] - para_l[7]) / (para_u[7] - s_temp[:, 7]))

s[:,:,0]=s_temp

forward_params = params = {'ncores': ncores,'index':index}
model = forward_model.Model(forward_params)

for t in range(len(Alpha)):
    sim_obs=forward_model.run_model(s[:,:,t],Num_ens) # shape of sim_obs (Num_ens,Num_obs)
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

sim_obs=model.run_model(s[:,:,len(Alpha)],t+1) # shape of sim_obs (Num_ens,Num_obs)
np.savetxt('./sim_obs' + str(len(Alpha)) + '.txt', np.mean(sim_obs,axis=0))

rmse = np.sqrt(np.mean((np.mean(sim_obs, axis=0) - obs.flatten()) ** 2))
print('RMSE ite_', t, ' : ', rmse)  # not the exact RMSE definition

nse = np.zeros(Num_ens)
for i in range(Num_ens):
    nse[i] = utility.calculate_nse(obs.reshape(-1), sim_obs[i, :].T)
nse_mean = np.mean(nse, 0)
print('NSE ite_',  len(Alpha), ' : ', nse_mean)

with open('metrics.txt', 'a') as f:
    f.write(f'Iteration {t+1}:\n')
    f.write(f'  RMSE: {rmse:.6f}\n')
    f.write(f'  NSE : {nse_mean:.6f}\n')
    f.write('\n')

savemat('results_esmda.mat',{'s':s,'sim_obs':sim_obs}) # sim_obs for the last step



