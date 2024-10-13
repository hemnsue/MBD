from car_lib import System,Params,State
#Vehicle Model
from car_lib import climb_resistance,climb_resistance_power,aerodynamic_resistance_power,aerodynamic_drag,rolling_resistance,cornering_resistance
#Transmission System Model
from car_lib import traction_power,traction_torque,force,shaft_angular_vel,shaft_power_em,shaft_torque
#Electric Machine Model
from car_lib import electric_machine
#Inverter Model
from car_lib import Inverter_output_power,Inverter_pow_loss,Inverter_power_loss_resistance,efficieny_inverter
#Battery Model
from car_lib import battery_spec,Capacity_Model,Vol_t_Res,elctric_model
#Boost Converter Model
from car_lib import boost_conv
#Rectifier Model
from car_lib import Rectifier
#import math and other required libraries
import math

Cdrag,Afront,mass,v_terminal,ccr,r=map(int,input("Enter coefficient of drag, frontal area of the vehicle,mass of the vehicle,terminal velocity of the vehicle,coefficient of cornering resistance of the vehicle , radius of the wheel"))
headwind,alpha,row_air=map(int,input("Enter the headwind,the angel of inclination, density of air"))
car_state=State(v_car=0,acc_car=0)
crr=0
Car=System(car_state=car_state,g=9.81,crr=crr,Cdrag=Cdrag,Afront=Afront,mass=mass,v_terminal=v_terminal,ccr=ccr,ft=0,r=r)
environment=System(headwind=headwind,alpha=alpha,row_air=row_air,eff_inv_nom=0.98)
electrical_machine=Params(Continuous_shaft_power=45,Peak_shaft_power=75,ns_max=8000,ns_corner=3000,ws_corner=0,ws_nom=0,ws_max=0,Ts_max=0,
P=18,Continuous_shaft_torque=150,Peak_shaft_torque=240,max_shaft_pow_cont_pow=0.94,max_shaft_pow_max_speed=0.90,Pem_max=0,Tc=0,Bv=0,Vth=1)

#Vehicle Model
def vehicle_model(Car,environment,dt):
    Car.car_state.v_car=Car.v_terminal
    Car.car_state.acc_car=Car.car_state.v_car/dt
    Car.crr=0.01*(1+3.6/100*Car.car_state.v_car)
    Car.ft=climb_resistance(m=Car.mass,alpha=environment.alpha)+(-1 if (Car.car_state.v_car+environment.headwind) <0 else 1)*aerodynamic_drag(Cw=Car.Cdrag,A=Car.Afront,v=Car.car_state.v_car,v_o=environment.headwind,row=environment.row_air)+(1 if Car.car_state.v_car>0 else -1)*rolling_resistance(m=mass,crr=Car.crr,alpha=Car.alpha)+Car.mass*Car.car_state.acc_car

#Transmission System
def transmission_model(Car,environment,dt,nsmax,Vcarmax,nTS):
    trc_torque=traction_torque(Car.ft,Car.rw)
    G=nsmax/Vcarmax*2*math.pi*Car.rw/60/1.1
    pt=traction_power(Car.ft,Car.car_state.v_car)
    Ts=shaft_torque(nTS,trc_torque,G,pt)
    w_w=Car.car_state.v_car/Car.rw
    ws=shaft_angular_vel(G,w_w)
    return Ts,ws

#Electric Machine

#Inverter Model
def Inverter_model(Car,environment,dt):
    PInvlossmax=(1-environment.eff_inv_nom)/environment.eff_inv_nom*electrical_machine.Pem_max
    Te_max=electrical_machine.Tc+electrical_machine.Bv*electrical_machine.ws_corner+electrical_machine.Ts_max
    Iq_max=2/3*2/electrical_machine.P
    R_Inv=PInvlossmax-6/math.pi*electrical_machine.Vth*Iq_max
    return Iq_max,R_Inv,Te_max

#final running of the model
#The European Drive Cycle
tv_car=[]
timestep=0.1
for i in tv_car:
    Car.v_terminal=i
    #Send to vehicle model to find the resisitive force
    vehicle_model(Car,environment,timestep)
    #Send the resisitve force with the transmission model to find the torque and angular velocity
    Ts,ws=transmission_model(Car,environment,timestep,electrical_machine.ns_max,Vcarmax,0.95)
    #Now model output is the Torque and angular velocity which is the input for the electric machine model
    electrical_machine.ws_corner=electrical_machine.ns_corner/60*2*math.pi
    electrical_machine.ws_nom=electrical_machine.Peak_shaft_power/electrical_machine.Continuous_shaft_torque
    electrical_machine.ws_max=electrical_machine.ns_max/60*2*math.pi
    aem=electrical_machine.Continuous_shaft_torque/electrical_machine.Peak_shaft_torque
    electrical_machine.Ts_max=Ts
    Ps_max=electrical_machine.Ts_max*electrical_machine.ws_corner
    if ws<=electrical_machine.ws_corner:
        Ts_limit=electrical_machine.Ts_max
    elif ws> electrical_machine.ws_corner:
        Ts_limit=Ps_max/ws
    Tc=0.02/ws*Ps_max/electrical_machine.max_shaft_pow_max_speed
    Bv=0.06/ws*Ps_max/electrical_machine.max_shaft_pow_max_speed
    Ts_count=electrical_machine.Ts_max/aem
    Te_cont=Tc+Bv*electrical_machine.ws_nom+Ts_count
    


    
    



