#%%
from electric_machine import Capacity_Model,battery_spec,Vol_t_Res,elctric_model
import pandas as pd
import matplotlib.pyplot as plt
#%%
def ploting(x,y,leg,linestyle="-",marker="o"):
    plt.plot(x,y,label=leg,linestyle=linestyle,marker=marker)
#%%
k=["C/5","C/2","C","2C"]
read_files1=pd.read_csv("2C.csv")
read_files2=pd.read_csv("C_0.csv")
read_files3=pd.read_csv("C_2.csv")
read_files4=pd.read_csv("C_5.csv")

ploting(read_files1["x"],read_files1["y"],k[3])
ploting(read_files2["x"],read_files2["y"],k[2])
ploting(read_files3["x"],read_files3["y"],k[1])
ploting(read_files4["x"],read_files4["y"],k[0])
#%%
Max_vol,Nom_vol,Min_vol,cap_1h,Nom_1h_dis,Max_pulse_dis=battery_spec()
currents=[1.4,3.5,7.0,14.0]

for current in currents:
    voltage=[]
    capacity=[]
    DOD=0
    time1=cap_1h/current
    time_step=time1/100
    for i in range(500):
        DoD_Bat_expr_sub,SoC_Bat_expr_sub=Capacity_Model(DOD,cap_1h,current,Nom_1h_dis,0.95,time_step)
        Rbat_cell_diss,Vbat,Rbat_cell_cha=Vol_t_Res(DoD_Bat_expr_sub)
        v1=elctric_model(Vbat,Rbat_cell_diss,Rbat_cell_cha,current)
        #print(v1)
        voltage.append(v1)
        current_capacity=SoC_Bat_expr_sub*cap_1h
        capacity.append(cap_1h-current_capacity)
        if v1<2.5:
            break
        '''if current_capacity<=0:
            break'''
        #print(current_capacity)
        DOD=DoD_Bat_expr_sub
    ploting(capacity,voltage,leg="Dis_C_Cal"+str(current),linestyle="-",marker="x")
    print(current)
plt.xlabel("Capacity[Ah]")
plt.ylabel("Voltage[V]")
plt.legend()
plt.grid(True)
plt.show()


# %%
