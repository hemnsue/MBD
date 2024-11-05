from car_lib import System,Params,State
#Vehicle Model
from car_lib import climb_resistance,climb_resistance_power,aerodynamic_resistance_power,aerodynamic_drag,rolling_resistance,cornering_resistance

Cdrag,Afront,mass,v_terminal,ccr,Js=map(int,input("Enter coefficient of drag, frontal area of the vehicle,mass of the vehicle,terminal velocity of the vehicle,coefficient of cornering resistance of the vehicle, moment of inertia of the shaft"))
headwind,alpha,row_air=map(int,input("Enter the headwind,the angel of inclination, density of air"))
car_state=State(v_car=0,acc_car=0)
crr=0
Car=System(car_state=car_state,g=9.81,crr=crr,Cdrag=Cdrag,Afront=Afront,mass=mass,v_terminal=v_terminal,ccr=ccr,ft=0,r=0.2785)
environment=System(headwind=headwind,alpha=alpha,row_air=row_air,eff_inv_nom=0.98)
electrical_machine=Params(Continuous_shaft_power=45,Peak_shaft_power=75,ns_max=8000,ns_corner=3000,ws_corner=0,ws_nom=0,ws_max=0,Ts_max=0,phi_em_nom=0.55,Js=Js,eff_inv_nom=0.98,vth_inv=1,
P=18,Continuous_shaft_torque=150,Peak_shaft_torque=240,max_shaft_pow_cont_pow=0.94,max_shaft_pow_max_speed=0.90,Pem_max=0,Tc=0,Bv=0,Vth=1)

#Vehicle Model
def vehicle_model(Car,environment,dt):
    Car.car_state.v_car=Car.v_terminal
    Car.car_state.acc_car=Car.car_state.v_car/dt
    Car.crr=0.01*(1+3.6/100*Car.car_state.v_car)
    Car.ft=climb_resistance(m=Car.mass,alpha=environment.alpha)+(-1 if (Car.car_state.v_car+environment.headwind) <0 else 1)*aerodynamic_drag(Cw=Car.Cdrag,A=Car.Afront,v=Car.car_state.v_car,v_o=environment.headwind,row=environment.row_air)+(1 if Car.car_state.v_car>0 else -1)*rolling_resistance(m=mass,crr=Car.crr,alpha=Car.alpha)+Car.mass*Car.car_state.acc_car