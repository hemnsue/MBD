#For the elcectric machine modelling we define functions
'''def electric_machine(Rs1,Ld1,Lq1,We1,lamda_pm1,vd1,vq1,id1,iq1,t1,T_c1,Bv1,Js1,P1):
    Rs, Ld, Lq, we, lamda_pm = sp.symbols('Rs Ld Lq we lamda_pm')
    vd, vq = sp.symbols('vd vq')
    i_d, i_q = sp.symbols('i_d i_q', cls=sp.Function)
    t = sp.symbols('t')

    # Define the time-dependent functions
    i_d = i_d(t)
    i_q = i_q(t)

    # Define the derivatives
    di_d_dt = sp.diff(i_d, t)
    di_q_dt = sp.diff(i_q, t)

    # Define the equations
    vd_eq = sp.Eq(vd, Rs * i_d + Ld * di_d_dt - we * Lq * i_q)
    vq_eq = sp.Eq(vq, Rs * i_q + Lq * di_q_dt + we * Ld * i_d + we * lamda_pm)
    Pem_eq = sp.Eq(3/2 * (vd * i_d + vq * i_q))

    Js, Bv, T_c, T_s = sp.symbols('Js Bv T_c T_s')
    T_e, ps = sp.symbols('T_e ps')
    t = sp.symbols('t')

    # Define the time-dependent function
    ws = sp.Function('ws')(t)

    # Define the derivative
    dws_dt = sp.diff(ws, t)

    # Define the equations
    Te_eq = sp.Eq(T_e, Js * dws_dt + Bv * ws + T_c + T_s)
    ps_eq = sp.Eq(ps, T_s * ws)

    P = sp.symbols('P')

    Te_eq = sp.Eq(T_e, 1.5 * 0.5 * P * (lamda_pm * i_q + (Ld - Lq) * i_d * i_q))
    we_eq = sp.Eq(we, P / 2 * ws)'''

import sympy as sp
from sympy.abc import t
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

'''def Capacity_Model(DOD,ibateq,Qbat,ibat1,ibat,eff):
    DoD_Bat_ini, i_Bat_eq_cell, Q_Bat_1_cell = sp.symbols('DoD_Bat DoD_Bat_ini i_Bat_eq_cell Q_Bat_1_cell')
    I_Bat_1_cell, i_Bat_cell, eta_Bat_cha = sp.symbols('I_Bat_1_cell i_Bat_cell eta_Bat_cha')
    k_expr = sp.symbols('k_expr')

    # Depth of Discharge
    DoD_Bat_expr = DoD_Bat_ini + sp.integrate(i_Bat_eq_cell / Q_Bat_1_cell, t)
    SoC_Bat_expr = 1 - DoD_Bat_expr

    k_expr = sp.Piecewise(
    (1, i_Bat_cell <= I_Bat_1_cell),
    (1.125, i_Bat_cell > I_Bat_1_cell)
    )

    # Equivalent battery cell current (i_Bat_eq_cell)
    i_Bat_eq_cell_expr = sp.Piecewise(
        (I_Bat_1_cell * (i_Bat_cell / I_Bat_1_cell)**k_expr, i_Bat_cell >= 0),
        (eta_Bat_cha * i_Bat_cell, i_Bat_cell < 0)
    )
    # Substitute parameters with their values
    substitutions = {
        DoD_Bat_ini: DOD,
        i_Bat_eq_cell: ibateq,
        Q_Bat_1_cell: Qbat,
        i_Bat_cell: ibat1,
        I_Bat_1_cell: ibat,
        eta_Bat_cha:eff
    }
    DoD_Bat_expr_sub=DoD_Bat_expr.subs(substitutions)
    SoC_Bat_expr_sub=SoC_Bat_expr.subs(substitutions)
    k_expr_subs=k_expr.subs(substitutions)
    i_Bat_eq_cell_expr_subs=i_Bat_eq_cell_expr.subs(substitutions)
    return SoC_Bat_expr_sub,i_Bat_eq_cell_expr_subs
'''
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
def Capacity_Model1(DOD, Qbat, ibat1, ibat, eff, tess):
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

    # Depth of Discharge increment per time step
    delta_DoD_expr = i_Bat_eq_cell_expr / Q_Bat_1_cell * tess

    # New DoD and SoC after the time step
    DoD_Bat_expr = DoD_Bat_ini + delta_DoD_expr
    SoC_Bat_expr = 1 - DoD_Bat_expr

    # Apply substitutions to expressions
    substitutions = {
        DoD_Bat_ini: DOD,
        Q_Bat_1_cell: Qbat,
        i_Bat_cell: ibat1,
        I_Bat_1_cell: ibat,
        eta_Bat_cha: eff,
        t: tess
    }

    delta_DoD_sub = delta_DoD_expr.subs(substitutions)
    DoD_Bat_expr_sub = DoD_Bat_expr.subs(substitutions)
    SoC_Bat_expr_sub = SoC_Bat_expr.subs(substitutions)

    return DoD_Bat_expr_sub, SoC_Bat_expr_sub

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
