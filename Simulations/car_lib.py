import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from types import SimpleNamespace
from copy import copy
from pint import UnitRegistry
import math
import sympy as sp
from sympy.abc import t
Units=UnitRegistry()
second=Units.second
meter=Units.meter
kg=Units.kilogram
N=Units.newton
km=Units.kilometers
hr=Units.hour
class SettableNamespace(SimpleNamespace):
    """Contains a collection of parameters.

    Used to make a System object.

    Takes keyword arguments and stores them as attributes.
    """
    def __init__(self, namespace=None, **kwargs):
        super().__init__()
        if namespace:
            self.__dict__.update(namespace.__dict__)
        self.__dict__.update(kwargs)

    def get(self, name, default=None):
        """Look up a variable.

        name: string varname
        default: value returned if `name` is not present
        """
        try:
            return self.__getattribute__(name, default)
        except AttributeError:
            return default

    def set(self, **variables):
        """Make a copy and update the given variables.

        returns: Params
        """
        new = copy(self)
        new.__dict__.update(variables)
        return new

class System(SettableNamespace):
    ##System Object for defining the system 
    pass
class Params(SettableNamespace):
    """Contains system parameters and their values.

    Takes keyword arguments and stores them as attributes.
    """
    pass

def State(**variables):
    """Contains the values of state variables."""
    return pd.Series(variables, name='state')

def TimeSeries(*args, **kwargs):
    """Make a pd.Series object to represent a time series.
    """
    if args or kwargs:
        underride(kwargs, dtype=float)
        series = pd.Series(*args, **kwargs)
    else:
        series = pd.Series([], dtype=float)

    series.index.name = 'Time'
    if 'name' not in kwargs:
        series.name = 'Quantity'
    return series

def underride(d, **options):
    """Add key-value pairs to d only if key is not in d.

    If d is None, create a new dictionary.

    d: dictionary
    options: keyword args to add to d
    """
    if d is None:
        d = {}

    for key, val in options.items():
        d.setdefault(key, val)

    return d


def SweepSeries(*args, **kwargs):
    """Make a pd.Series object to store results from a parameter sweep.
    """
    if args or kwargs:
        underride(kwargs, dtype=float)
        series = pd.Series(*args, **kwargs)
    else:
        series = pd.Series([], dtype=np.float64)

    series.index.name = 'Parameter'
    if 'name' not in kwargs:
        series.name = 'Metric'
    return series


def climb_resistance(g=9.81*(meter/second**2),m=0*kg,alpha=0,p=0):
    p=p/100
    if alpha==0 and p==0:
        F_st=0*N
    elif alpha>0:
        F_st=m*g*math.sin(math.radians(alpha))
    elif p<.20 and p>0 and alpha==0:
        F_st=m*g*math.tan(math.radians(p))
    elif p>.20 and alpha==0:
        F_st=m*g*math.sin((math.atan(p)))
    return F_st

def climb_resistance_power(resistance_weight_in_newtons,speeds_ms):
    P_climb_resistance=(resistance_weight_in_newtons.to(N)*speeds_ms.to(meter/second)).to(Units.kilowatt)
    return P_climb_resistance

def aerodynamic_drag(Cw=0,A=0*meter**2,v=0*km/hr,v_o=0*km/hr,row=1.204*kg/(meter**3)):
    F_l=.5*row.to(kg/meter**3)*Cw*A.to(meter**2)*(v.to(meter/second)+v_o.to(meter/second))**2
    return F_l

def aerodynamic_resistance_power(F_l=0*N,speed_ms=0*meter/second):
    P_aerodynaic_resistance=(F_l.to(N)*speed_ms.to(meter/second)).to(Units.kilowatt)
    return P_aerodynaic_resistance.to(N)

def rolling_resistance(m=0*kg,g=9.81*meter/second**2,crr=0,alpha=0):
    F_ro=m*g*math.cos(math.radians(alpha))*crr
    return F_ro.to(N)

def cornering_resistance(m=0*kg,g=9.81*meter/second**2,ccr=0,alpha=0):
    F_ro=m*g*math.cos(math.radians(alpha))*ccr
    return F_ro.to(N)

def force(m=0*kg,acc=0*meter/second**2):
    return (m*acc).to(N)

def traction_torque(ft=0*N,rw=0*meter):
    return (ft*rw).to(N/meter)

def traction_power(ft=0*N,vcar=0*meter/second):
    return ft*vcar

def shaft_torque(effciency,traction_torque,Gear_ratio_differential,traction_power):
    if traction_power<0:
        return (effciency*traction_torque/Gear_ratio_differential).to(N/meter)
    elif traction_power>=0: 
        return (traction_torque/effciency*Gear_ratio_differential).to(N/meter)
    
def shaft_power_em(shaft_torque,angular_vel_em):
    return shaft_torque*angular_vel_em

def shaft_angular_vel(Gear_ratio_differential,angular_vel_wheel):
    return Gear_ratio_differential*angular_vel_wheel

def Inverter_pow_loss(Vp,Rq_Inv,Ip,fi,Vq_th_v,Rd_Inv,Vd_th_v,Vbat):
    mi=2*Vp/Vbat
    Pq_Inv=(1/8+mi/(3*math.pi))*Rq_Inv*Ip**2+(1/(2*math.pi)+mi/8*math.cos(math.radians(fi))*Vq_th_v)
    Pd_Inv=(1/8-mi/(3*math.pi))*Rd_Inv*Ip**2+(1/(2*math.pi)-mi/8*math.cos(math.radians(fi))*Vd_th_v)
    PInv_ls=6*(Pq_Inv+Pd_Inv)
    return PInv_ls

def Inverter_power_loss_resistance(R_inv,Ip,V_th_inv):
    PInv_loss=3/2*R_inv*Ip**2+6/math.pi*V_th_inv*Ip
    return PInv_loss

def Inverter_output_power(vbat=0,i_INV=0,PEM=0,PInv_Loss=0):
    if PInv_Loss==0 or PEM==0:
        return vbat*i_INV
    else:
        return PEM+PInv_Loss
    
def efficieny_inverter(PEM,PInv):
    if PEM >=0:
        return PEM/PInv
    else:
        return PInv/PEM

def boost_conv(Vbat,ibc,Rbc,irf,VthBc,Vrf=0,i=0):
    if i==0:
        PBC=Vbat*ibc
        PLoss=Rbc*irf**2+VthBc*irf
        Prf=PBC+PLoss
        return Prf,PBC,PLoss
    if i==1:
        Prf=Vrf*irf
        PLoss=Rbc*irf**2+VthBc*irf
        PBC=Prf-PLoss
        return Prf,PLoss,PBC
 
def Rectifier(Ig,Vll,Rf,Vth):
    irf=Ig(3/2)**.5
    Vrf=3*2**.5/math.pi*Vll-2*Rf*irf-2*Vth
    Prf=Vrf*irf
    Pgrid=3*2**.5/math.pi*Vll*irf
    PrfL=2*Rf*irf**2+2*Vth*irf
    return Prf,Pgrid,PrfL

def electric_machine(Rs1, Ld1, Lq1, We1, lamda_pm1, vd1, vq1, id1, iq1, t1, T_c1, Bv1, Js1, P1):
    # Define symbols
    Rs, Ld, Lq, we, lamda_pm = sp.symbols('Rs Ld Lq we lamda_pm')
    vd, vq = sp.symbols('vd vq')
    i_d, i_q = sp.symbols('i_d i_q', cls=sp.Function)
    t = sp.symbols('t')
    
    # Define time-dependent functions
    i_d = i_d(t)
    i_q = i_q(t)

    # Define the derivatives
    di_d_dt = sp.diff(i_d, t)
    di_q_dt = sp.diff(i_q, t)

    # Define the equations
    vd_eq = sp.Eq(vd, Rs * i_d + Ld * di_d_dt - we * Lq * i_q)
    vq_eq = sp.Eq(vq, Rs * i_q + Lq * di_q_dt + we * Ld * i_d + we * lamda_pm)
    
    
    Pem_eq =3/2 * (vd * i_d + vq * i_q)

    Js, Bv, T_c, T_s = sp.symbols('Js Bv T_c T_s')
    T_e, ps = sp.symbols('T_e ps')

    # Define the time-dependent function
    ws = sp.Function('ws')(t)

    # Define the derivative
    dws_dt = sp.diff(ws, t)

    # Define the equations
    Te_eq = sp.Eq(T_e, Js * dws_dt + Bv * ws + T_c + T_s)
    ps_eq = sp.Eq(ps, T_s * ws)

    # Define power equations
    P = sp.symbols('P')  # Define P here
    Te_eq = sp.Eq(T_e, 1.5 * 0.5 * P * (lamda_pm * i_q + (Ld - Lq) * i_d * i_q))
    we_eq = we, P / 2 * ws
    

    # Substitute parameters with their values
    substitutions = {
        Rs: Rs1,
        Ld: Ld1,
        Lq: Lq1,
        we: We1,
        lamda_pm: lamda_pm1,
        vd: vd1,
        vq: vq1,
        i_d: id1,
        i_q: iq1,
        T_c: T_c1,
        Bv: Bv1,
        Js: Js1,
        P: P1,
        t:t1
    }

    # Substitute and simplify the equations
    vd_eq_substituted = vd_eq.subs(substitutions)
    vq_eq_substituted = vq_eq.subs(substitutions)
    Te_eq_substituted = Te_eq.subs(substitutions)
    ps_eq_substituted = ps_eq.subs(substitutions)

    # Return substituted equations
    return vd_eq_substituted, vq_eq_substituted, Te_eq_substituted, ps_eq_substituted,we_eq,Pem_eq

def Capacity_Model(DOD, Qbat, ibat1, ibat, eff,tess):
    # Define symbolic variables
    DoD_Bat_ini, Q_Bat_1_cell = sp.symbols('DoD_Bat_ini Q_Bat_1_cell')
    I_Bat_1_cell, i_Bat_cell, eta_Bat_cha, t = sp.symbols('I_Bat_1_cell i_Bat_cell eta_Bat_cha t')
    
    # Peukert number (k)
    k_expr = sp.Piecewise(
        (1, i_Bat_cell <= I_Bat_1_cell),
        (1.125, i_Bat_cell > I_Bat_1_cell)
    )

    # Equivalent battery cell current (i_Bat_eq_cell)
    i_Bat_eq_cell_expr = sp.Piecewise(
        (I_Bat_1_cell * (i_Bat_cell / I_Bat_1_cell)**k_expr, i_Bat_cell >= 0),
        (eta_Bat_cha * i_Bat_cell, i_Bat_cell < 0)
    )
    
    # Depth of Discharge
    DoD_Bat_expr = DoD_Bat_ini + sp.integrate(i_Bat_eq_cell_expr / Q_Bat_1_cell, t)
    SoC_Bat_expr = 1 - DoD_Bat_expr

    # Apply substitutions to expressions
    substitutions = {
        DoD_Bat_ini: DOD,
        Q_Bat_1_cell: Qbat,
        i_Bat_cell: ibat1,
        I_Bat_1_cell: ibat,
        eta_Bat_cha: eff,
        t:tess
    }
    i_Bat_eq_cell_expr_sub=i_Bat_eq_cell_expr.subs(substitutions)
    DoD_Bat_expr_sub = DoD_Bat_expr.subs(substitutions)
    SoC_Bat_expr_sub = SoC_Bat_expr.subs(substitutions)
    #print(i_Bat_eq_cell_expr_sub,DoD_Bat_expr_sub,SoC_Bat_expr_sub)

    return DoD_Bat_expr_sub,SoC_Bat_expr_sub

def battery_spec():
    Max_vol=4.2
    Nom_vol=3.7
    Min_vol=2.5
    cap_1h=7
    Nom_1h_dis=7
    Max_pulse_dis=28
    return Max_vol,Nom_vol,Min_vol,cap_1h,Nom_1h_dis,Max_pulse_dis

def Vol_t_Res(Dodbat):
    Rbat_cell_diss=-634.0*Dodbat**10+2941*Dodbat**9-5790.6*Dodbat**8+6297.4*Dodbat**7-4132.1*Dodbat**6+1677.7*Dodbat**5-416.4*Dodbat**4+60.5*Dodbat**3-4.8*Dodbat**2+0.2*Dodbat**1+0
    Vbat=-8848*(Dodbat)**10+40727*(Dodbat)**9-79586*(Dodbat)**8+86018*Dodbat**7-56135*Dodbat**6-5565*Dodbat**5+784*Dodbat**4-25*Dodbat**3+55*Dodbat**2+4
    Rbat_cell_cha=2056*Dodbat**10-9176*Dodbat**9+17147*Dodbat**8-17330*Dodbat**7+10168*Dodbat**6-3415*Dodbat**5+578*Dodbat**4+25*Dodbat**3+3*Dodbat**3
    print(Vbat)
    return Rbat_cell_diss,Vbat,Rbat_cell_cha

def elctric_model(vBatcell,Rbatinit_cell_dis,Rbatinit_cell_cha,ibatcell):
    if ibatcell>=0:
        return (vBatcell-Rbatinit_cell_dis*ibatcell)
    else:
        return (vBatcell-Rbatinit_cell_cha*ibatcell)
    
def Auxilary_Loads(Radio,Heating_Ventilation,Lights,):
    return Radio+Heating_Ventilation+Lights

