import numpy as np
import pandas as pd
import subprocess
import re
import h5py
from scipy.optimize import curve_fit
import os
import sys
i = int(sys.argv[1])
param=np.loadtxt('../Site1_param'+str(i)+'.txt')
file_path = 'ats_vis_data.VisIt.xmf'

# Read the file content
with open(file_path, 'r') as file:
    content = file.read()

# Regular expression to match numbers between 'h5' and 'xmf'
pattern = r"h5\.(\d+)\.xmf"
matches = re.findall(pattern, content)

# Convert matches to integers
numbers = [int(match) for match in matches]
loc=pd.read_csv('../data/Site_1_mesh_long.csv').iloc[:,[0,2]]
for i in range(len(numbers)):
    fin=loc.copy()
    temp=loc.copy()
    df=h5py.File('ats_vis_data.h5', 'r')
    fin['porosity']=df['base_porosity'][str(numbers[i])]
    fin['U']=df['darcy_velocity.x'][str(numbers[i])]
    fin['W']=df['darcy_velocity.z'][str(numbers[i])]
    fin['sat']=df['saturation_liquid'][str(numbers[i])]
    fin['time']=i
    temp['h']=df['pressure'][str(numbers[i])]
    if i==0:
        out=fin.copy()
        pressure=temp.copy()
        continue
    out=pd.concat([out,fin])
    pressure=pd.concat([pressure,temp])
#Assign homogeneous resistivity from field data
df=out.copy()
df['cond']=0
df['cond'][df["porosity"]>=0.1]=1/param[6]# 40 original used
df['cond'][df["porosity"]<0.1]=1/100
df1=df.iloc[:,[0,1,6,3,4,2,5,7]]
df1.columns = ['X', 'Z', 't', 'U','W', 'Por','sat','cond']
#top soil function to change conductivity with saturation
def model2(por_sat, surf_cond):
    por,sat=por_sat
    return (por**2 *0.015* sat**2)+surf_cond
params, covariance = curve_fit(model2, (df1[(df1['t']==max(df1.t))&(df1['Por']>0.07)]['Por'].values,
                                       df1[(df1['t']==max(df1.t))&(df1['Por']>0.07)]['sat'].values),
                               df1[(df1['t']==max(df1.t))&(df1['Por']>0.07)]['cond'].values)
surf_cond=params
fluid_cond=0.015
df1['cond'][df1['Por']>0.07]=model2((df1[df1['Por']>0.07]['Por'].values,
                                       df1[df1['Por']>0.07]['sat'].values),surf_cond)
df1["Perm"]=0
df1['Perm'][df1["Por"]>=0.1]=param[1]# 40 original used
df1['Perm'][df1["Por"]<0.1]=param[0]
df1['m']=1.5
df1['Qv']=0
#Calculating Qv from REV method
df1['Qv']=param[5]/df1['sat']
df1.to_csv('data_set_edit.txt',index=False)
