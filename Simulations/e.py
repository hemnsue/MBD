from electric_machine import Capacity_Model,battery_spec,Vol_t_Res,elctric_model
import pandas as pd
import matplotlib.pyplot as plt

def ploting(x,y,leg,linestyle="-",marker="o"):
    plt.plot(x,y,label=leg,linestyle=linestyle,marker=marker)

Max_vol,Nom_vol,Min_vol,cap_1h,Nom_1h_dis,Max_pulse_dis=battery_spec()
voltage=[]
capacity=[]
current=1.4
#time=int(cap_1h/current)
#time_steps=time*60
time_step=0.1
DOD=0
while DOD<1:
    DoD_Bat_expr_sub,SoC_Bat_expr_sub=Capacity_Model(DOD,cap_1h,current,Nom_1h_dis,0.95,time_step)
    Rbat_cell_diss,Vbat,Rbat_cell_cha=Vol_t_Res(DoD_Bat_expr_sub)
    v1=elctric_model(Vbat,Rbat_cell_diss,Rbat_cell_cha,current)
    DOD=DoD_Bat_expr_sub
    print(v1)
    voltage.append(v1)
    capacity.append(cap_1h-SoC_Bat_expr_sub*cap_1h)
    if v1<=2.4:
        break
ploting(capacity,voltage,leg="Dis_C_Cal"+str(current),linestyle="-",marker="x")
plt.xlabel("Capacity[Ah]")
plt.ylabel("Voltage[V]")
plt.legend()
plt.grid(True)
plt.show()
