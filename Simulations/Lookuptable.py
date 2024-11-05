#%%
import numpy as np
import pandas as pd
from pint import UnitRegistry
from math import sin,cos,tan,atan,degrees,radians
#%%
Units=UnitRegistry()
second=Units.second
meter=Units.meter
kg=Units.kilogram
N=Units.newton
km=Units.kilometers
hr=Units.hour
#%%

def climb_resistance(g=9.81*(meter/second**2),m=0,alpha=0,p=0):
    p=p/100
    if alpha==0 and p==0:
        F_st=0*N
    elif alpha>0:
        F_st=m*g*sin(radians(alpha))
    elif p<.20 and p>0 and alpha==0:
        F_st=m*g*tan(radians(p))
    elif p>.20 and alpha==0:
        F_st=m*g*sin((atan(p)))
    return F_st

#j=climb_resistance(9.81*meter/(second**2),1000*kg,3,0)
#print(j)

# %%
k=np.linspace(500,3500,21)*kg
j=np.linspace(0,45,45)
inclination=np.tan(np.radians(j))
final2 = pd.Series([inclinations*100 for inclinations in inclination], index=j)
speeds=[20,30,40,50,60]*km/hr
speeds_ms=speeds.to(meter/second)
for i in k:
    l=[]
    v_20=[]
    v_30=[]
    v_40=[]
    v_50=[]
    v_60=[]
    for n in j:
        resistance_weight=climb_resistance(9.81*meter/(second**2),i,n,0)
        resistance_weight_in_newtons=resistance_weight.to('newton')
        l.append(resistance_weight_in_newtons)
        powerinw=resistance_weight_in_newtons*speeds_ms
        power_in_KW=powerinw.to(Units.kilowatt)
        power_in_KW=[f'{i:.2f}' for i in power_in_KW]

        v_20.append(power_in_KW[0])
        v_30.append(power_in_KW[1])
        v_40.append(power_in_KW[2])
        v_50.append(power_in_KW[3])
        v_60.append(power_in_KW[4])

    final = pd.Series([f'{resistance_weight_in_newtons:.2f}' for resistance_weight_in_newtons in l], index=j)
    speed_series1=pd.Series(v_20,index=j)
    speed_series2=pd.Series(v_30,index=j)
    speed_series3=pd.Series(v_40,index=j)
    speed_series4=pd.Series(v_50,index=j)
    speed_series5=pd.Series(v_60,index=j)

    result=pd.concat([final2,final,speed_series1,speed_series2,speed_series3,speed_series4,speed_series5],axis=1)
    result.to_excel('concatenated_series+'+str(i)+'.xlsx', index=True)

#%%
'''result
#%%
j=np.linspace(0,45,45)
speeds=[20,30,40,50,60]*km/hr
speeds_ms=speeds.to(meter/second)'''

#%%
'''l=[]
for k in j:
    resistance_weight=climb_resistance(9.81*meter/(second**2),1000*kg,k,0)
    resistance_weight_in_newtons=resistance_weight.to('newton')
    l.append(resistance_weight_in_newtons)
    power_in_KW=resistance_weight_in_newtons*speeds/3600
print(power_in_KW)
#final = pd.Series([f'{resistance_weight_in_newtons:.2f}' for resistance_weight_in_newtons in l], index=j)
#final2 = pd.Series([inclinations*100 for inclinations in inclination], index=j)
#result=pd.concat([final2,final],axis=1)
#result2=pd.concat([result,speeds],axis=0)'''
#%%
#result
'''# %%
        powerinw=resistance_weight_in_newtons*speeds_ms
        power_in_KW=powerinw.to(Units.kilowatt)
        power_in_KW=[f'{i:.2f}' for i in power_in_KW]'''
#%%
'''resistance_weight_in_newtons=500*N
powerir=resistance_weight_in_newtons*speeds_ms
power_in_KW=powerir.to(Units.kilowatt)
print(power_in_KW[4])'''
#%%
