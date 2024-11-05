
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


Max_vol,Nom_vol,Min_vol,cap_1h,Nom_1h_dis,Max_pulse_dis=battery_spec()
print(Max_vol,Nom_vol,Min_vol,cap_1h,Nom_1h_dis,Max_pulse_dis)
currents=[1.4,3.5,7.0,14.0]
timestep=0.1
total_time=7.0/max(currents)

for current in currents:
    DOD=0
    capacity=[]
    voltage=[]
    time=0
    while DOD <= 1 and time<=total_time:
        Soc,i_Bat_eq=Capacity_Model(DOD,0,cap_1h,current,Nom_1h_dis,0.95)
        print(Soc)
        Soc=float(Soc)
        DOD=1-Soc
        #DOD += (i_Bat_eq / cap_1h) * timestep  # Integrate DoD
        print(DOD)
        Rbat_dis,Vbat,Rbat_cha=Vol_t_Res(DOD)
        V_out=elctric_model(Vbat,Rbat_dis,Rbat_cha,current)
        V_out=float(V_out)
        capacity.append(time*current)
        voltage.append(V_out)
        time+=timestep
    ploting(capacity,voltage,leg="Dis_C_Cal"+str(current),linestyle="-",marker="x")
plt.xlabel("Capacity[Ah]")
plt.ylabel("Voltage[V]")
plt.legend()
plt.grid(True)
plt.show()