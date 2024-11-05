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
from car_lib import Rectifier,Auxilary_Loads
#import math and other required libraries
import math

Cdrag,Afront,mass,v_terminal,ccr,Js=map(int,input("Enter coefficient of drag, frontal area of the vehicle,mass of the vehicle,terminal velocity of the vehicle,coefficient of cornering resistance of the vehicle, moment of inertia of the shaft"))
headwind,alpha,row_air=map(int,input("Enter the headwind,the angel of inclination, density of air"))
car_state=State(v_car=0,acc_car=0)
crr=0
Car=System(car_state=car_state,g=9.81,crr=crr,Cdrag=Cdrag,Afront=Afront,mass=mass,v_terminal=v_terminal,ccr=ccr,ft=0,r=0.2785)
environment=System(headwind=headwind,alpha=alpha,row_air=row_air,eff_inv_nom=0.98)
electrical_machine=Params(Continuous_shaft_power=45,Peak_shaft_power=75,ns_max=8000,ns_corner=3000,ws_corner=0,ws_nom=0,ws_max=0,Ts_max=0,phi_em_nom=0.55,Js=Js,eff_inv_nom=0.98,vth_inv=1,
P=18,Continuous_shaft_torque=150,Peak_shaft_torque=240,max_shaft_pow_cont_pow=0.94,max_shaft_pow_max_speed=0.90,Pem_max=0,Tc=0,Bv=0,Vth=1)
battery=Params(Vbat_max_cell=4.2,Vbat_nom_cell=3.7,Vbat_min_cell=2.5,Q1_cell=7,I_bat1cell=7,ibatcell=28,v_RF=0,i_rf=0,iBat_cell=28,
RBat_cell_dis=0,RBat_cell_cha=0,Dod=0,SOC=1,ibat=0,nbat_cha=0.95,iBat1_cell=7,Vbat=0,Nbatp=5,Nbats=216,iBC=0,i_Bat_cha_max=0,
i_Bat_cell_cha_max=0,vbat_int_cell=0,effbat_cha=0.95,i_bat_cha_max=0,iBC=0,P_BC=0,vth_bc=1.5)

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

#Inverter Model
def Inverter_model(Car,environment,dt):
    PInvlossmax=(1-environment.eff_inv_nom)/environment.eff_inv_nom*electrical_machine.Pem_max
    Te_max=electrical_machine.Tc+electrical_machine.Bv*electrical_machine.ws_corner+electrical_machine.Ts_max
    Iq_max=2/3*2/electrical_machine.P
    R_Inv=PInvlossmax-6/math.pi*electrical_machine.Vth*Iq_max
    return Iq_max,R_Inv,Te_max

#final running of the _nommodel
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
    #Relationship between maximum and continuous shaft torque
    aem=electrical_machine.Continuous_shaft_torque/electrical_machine.Peak_shaft_torque
    #Only possible to have max shaft torque as long as the product of the shaft torque and angular velocity is below the maximum shaft torque due to the voltage induced by the permanent magnet
    electrical_machine.Ts_max=Ts
    Ps_max=electrical_machine.Ts_max*electrical_machine.ws_corner
    if ws<=electrical_machine.ws_corner:
        Ts_limit=electrical_machine.Ts_maxshaft
    elif ws> electrical_machine.ws_corner:
        Ts_limit=Ps_max/ws
    #Finding the columb torque and viscious friction taking into consideration the power loss
    Tc=0.02/ws*Ps_max/electrical_machine.max_shaft_pow_max_speed
    Bv=0.06/ws*Ps_max/electrical_machine.max_shaft_pow_max_speed
    #Nominal Electro mechanical torque
    Ts_count=electrical_machine.Ts_max/aem
    Te_cont=Tc+Bv*electrical_machine.ws_nom+Ts_count
    #Finding the modulation index of the motor, as machine is designed at nominal speed and max power with min bus voltage. At minimum bus voltage, machine should be abel to run at max speed with modulation index=1, because its designed at nominla speed but at min baattery voltage, the modulation index is-
    mi_nom=electrical_machine.ws_nom/electrical_machine.ws_max #orginal modulation index
    #Voltage of the machine 
    Vp_nom=mi_nom*540/2
    vd_nom=-Vp_nom*math.sin(electrical_machine.phi_em_nom)
    vq_nom=Vp_nom*math.cos(electrical_machine.phi_em_nom)
    Pem_max=Ps_max/electrical_machine.max_shaft_pow_cont_pow
    Iq_count=(2/3)*(Pem_max/vq_nom)
    #For further caluculations, Permanent magnet flux linkage,Angular velocity of the stator,stator phase resistance
    lambda_pm=2/3*2/electrical_machine.P*Te_cont/Iq_count
    we_nom=electrical_machine.ws_nom*electrical_machine.P/2
    Lq=-vd_nom/(we_nom*Iq_count)
    Rs=vq_nom-we_nom*lambda_pm/Iq_count
    #Using the electrical machine model for finding the Pem max
    vd,vq,Te,ps,Pem=electric_machine(Rs,0,Lq,lambda_pm,0,Iq_count,timestep,Tc,electrical_machine.Ts_max,Bv,Js,electrical_machine.P)

    #For the Inverter modelling
    Te_max=Tc+Bv*electrical_machine.ws_corner+electrical_machine.Ts_max

    Iq_max=(2/3)(*2/electrical_machine.P)*(Te_max/lambda_pm)

    Pinv_loss_max=(1-electrical_machine.eff_inv_nom)/electrical_machine.eff_inv_nom*Pem_max

    Rinv=((Pinv_loss_max)-(6/math.pi*electrical_machine.vth_inv*Iq_max))/(3/2*Iq_max**2)

    Pinv_lss=Inverter_pow_loss(Vp_nom,Rinv,Iq_max,electrical_machine.phi_em_nom,electrical_machine.vth_inv,Rinv,electrical_machine.vth_inv,battery.Vbat)

    Pinv_lss=3/2*(Rinv*Iq_max**2)+6/(math.pi*electrical_machine.vth_inv*Iq_max)

    pinv=Pem+Pinv_lss

    iInv=pinv/battery.Vbat
    nth=efficieny_inverter(Pem,pinv)

    #Braking Resistor Model
    loads=Auxilary_Loads(52,489,316)
    i_Aux=loads/battery.Vbat
    #Now we use the electric model for further calculations
    #Modelling the battery
    #Use the capacity model to find the DOD and SOC first
    #value of ibatcell is 28, use this to find vbat, and the values required to calulate x
    battery.Dod,battery.SOC=Capacity_Model(battery.Dod,battery.Q1_cell,battery.ibatcell,battery.I_bat1cell,battery.effbat_cha,timestep)
    battery.RBat_cell_dis,battery.vbat_int_cell,battery.RBat_cell_cha=Vol_t_Res(battery.Dod)
    x=(battery.Vbat_max_cell-battery.vbat_int_cell)/battery.R_Bat_cell_cha
    if x<= battery.I_bat1cell:
        battery.i_Bat_cell_cha_max=x
    else:
        battery.i__Bat_cell_cha_max=battery.I_bat1cell
    battery.Vbat=battery.Nbats*battery.vbat_int_cell
    battery.ibat=battery.Nbatp*battery.iBat_cell
    battery.i_bat_cha_max=battery.Nbatp*battery.i_Bat_cell_cha_max
    #Calculations needed for the boost converter and the rectifier
    battery.iBC=battery.i_bat_cha_max
    battery.P_BC=battery.Vbat*battery.iBC
    #to calculate vrf and irf we need Irf so we asswume Irf_max=Irf,sooo.............................aaaaaaaaaaaaaahhhhhhhhhhhhhhhhhhhhh
    Irf=19.6
    Pgrid=3(2)**.5*400/math.pi*Irf

    P_bc=battery.Vbat*battery.iBC
    battery.i_rf=-(battery.vth_bc-vrf)-((battery.vth_bc-vrf)**2-4*battery.P_BC*475)**.5

    P_Loss_bc=475*

