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
file_path = 'ats_vis_data.VisIt.xmf'

# Read the file content
with open(file_path, 'r') as file:
    content = file.read()

# Regular expression to match numbers between 'h5' and 'xmf'
pattern = r"h5\.(\d+)\.xmf"
matches = re.findall(pattern, content)

# Convert matches to integers
numbers = [int(match) for match in matches]
loc=pd.read_csv('../data/mesh_cnt3.csv').iloc[:,[0,2]]
for i in range(len(numbers)):
    fin=loc.copy()
    temp=loc.copy()
    df=h5py.File('ats_vis_data.h5', 'r')
    fin['porosity']=df['base_porosity'][str(numbers[i])]
    fin['U']=df['darcy_velocity.0'][str(numbers[i])]
    fin['W']=df['darcy_velocity.2'][str(numbers[i])]
    fin['k']=df['permeability'][str(numbers[i])]
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
df['cond'][df["porosity"]>=0.4]=1/40# 40 original used
df['cond'][df["porosity"]<0.4]=1/800
df1=df.iloc[:,[0,1,7,3,4,2,6,8,5]]
df1.columns = ['X', 'Z', 't', 'U','W', 'Por','sat','cond','Perm']
df1['m']=0
def model1(por_sat, m):
    por,sat=por_sat
    return (por**m *0.08* sat**2)
params, covariance = curve_fit(model1, (df1[(df1['t']==170)&(df1['Por']<0.07)]['Por'].values,
                                    df1[(df1['t']==170)&(df1['Por']<0.07)]['sat'].values),
                            df1[(df1['t']==170)&(df1['Por']<0.07)]['cond'].values)
m=params
m1=params
fluid_cond=0.08
surf_cond=0
df1['cond'][df1['Por']<0.07]=model1((df1[df1['Por']<0.07]['Por'].values,
                                    df1[df1['Por']<0.07]['sat'].values),m)
df1['m'][df1['Por']<0.07]=float(m)
def model2(por_sat, surf_cond):
    por,sat=por_sat
    return (por**1.5 *0.08* sat**2)+surf_cond
params, covariance = curve_fit(model2, (df1[(df1['t']==170)&(df1['Por']>0.07)]['Por'].values,
                                    df1[(df1['t']==170)&(df1['Por']>0.07)]['sat'].values),
                            df1[(df1['t']==170)&(df1['Por']>0.07)]['cond'].values)
surf_cond=params
surf_cond2=params
fluid_cond=0.08
m=1.5
df1['cond'][df1['Por']>0.07]=model2((df1[df1['Por']>0.07]['Por'].values,
                                    df1[df1['Por']>0.07]['sat'].values),surf_cond)
df1['m'][df1['Por']>0.07]=1.5
df1['Qv']=0
pressure.h=pressure.h-101325
m_vg=(1.426455636-1)/1.426455636 #Soldi et al, 2019
alpha=4.9e-05
pressure['sat']=0
pressure['sat']=-0.1+(1+abs(alpha*pressure['h'])**1.426455636)**-m_vg
pressure['sat'][pressure['h']>0]=1
rel_perm=pressure['sat']**0.5*(1-(1-pressure['sat']**(1/m_vg))**m_vg)**2
#Calculating Qv from REV method
e0 = 1.602e-19   # Elementary charge (C)   
C0=800*1.3e-5 # fluid conc. from 0.08 S/m using eqn from Griffin and Jurinak
E=80.1*8.854e-12 # F/m
kB=1.381e-23
T=273.15+20
tau=df1["Por"]**(1-df1['m'])
phi=df1["Por"]
k=df1['Perm']
zeta=-0.00643+0.02085*np.log10(C0)
df1['Qv']=(E*(-zeta-zeta**3*(((e0) / ( kB * T))**2)/54)*(1 / tau**2) * (phi / k))*pressure['sat']/rel_perm #Soldi et al, 2019
df1.to_csv('data_set_edit_short.txt',index=False)
with zipfile.ZipFile('data_set_edit_short.zip', 'w',zipfile.ZIP_DEFLATED) as myzip:
    myzip.write('data_set_edit_short.txt')
with open("matlab_exe.txt", "w") as f:
    f.write("done")
with open("matlab_signal.txt", "w") as f:
    f.write("wait")
