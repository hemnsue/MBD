import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# Define your existing functions
def Capacity_Model(DOD, Qbat, ibat1, ibat, eff, tess):
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
        t: tess
    }
    DoD_Bat_expr_sub = DoD_Bat_expr.subs(substitutions)
    SoC_Bat_expr_sub = SoC_Bat_expr.subs(substitutions)

    return DoD_Bat_expr_sub, SoC_Bat_expr_sub

def Vol_t_Res(Dodbat):
    Rbat_cell_diss = -634.0*Dodbat**10 + 2941*Dodbat**9 - 5790.6*Dodbat**8 + 6297.4*Dodbat**7 - 4132.1*Dodbat**6 + 1677.7*Dodbat**5 - 416.4*Dodbat**4 + 60.5*Dodbat**3 - 4.8*Dodbat**2 + 0.2*Dodbat + 0
    Vbat = -8848*Dodbat**10 + 40727*Dodbat**9 - 79586*Dodbat**8 + 86018*Dodbat**7 - 56135*Dodbat**6 - 5565*Dodbat**5 + 784*Dodbat**4 - 25*Dodbat**3 + 55*Dodbat**2 + 4
    Rbat_cell_cha = 2056*Dodbat**10 - 9176*Dodbat**9 + 17147*Dodbat**8 - 17330*Dodbat**7 + 10168*Dodbat**6 - 3415*Dodbat**5 + 578*Dodbat**4 + 25*Dodbat**3 + 3*Dodbat**3
    return Rbat_cell_diss, Vbat, Rbat_cell_cha

# Battery Specifications
Qbat = 7.0  # Battery capacity in Ah
timestep = 0.1  # Time step in hours
total_time = 5  # Total discharge time in hours
currents = [1.4, 3.5, 7.0, 14.0]  # Currents in Amperes

# Initialize storage for results
results = {current: {'time': [], 'voltage': [], 'capacity': []} for current in currents}

# Simulation for each current
for current in currents:
    DOD = 0  # Initial DoD
    time_steps = int(total_time / timestep)
    
    for step in range(time_steps):
        tess = step * timestep
        DOD, SoC = Capacity_Model(DOD, Qbat, current, current, 1.0, tess)
        
        # Calculate voltage from the depth of discharge
        voltage = Vol_t_Res(DOD)[1]  # Get voltage from Vol_t_Res
        
        remaining_capacity = Qbat * (1 - DOD)  # Remaining capacity
        
        # Store results
        results[current]['time'].append(tess)
        results[current]['voltage'].append(voltage)
        results[current]['capacity'].append(remaining_capacity)

# Plot results
plt.figure(figsize=(12, 8))
for current in currents:
    plt.plot(results[current]['capacity'], results[current]['voltage'], label=f'Current: {current} A')

plt.title('Voltage vs Remaining Capacity')
plt.xlabel('Remaining Capacity (Ah)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid()
plt.ylim(2.5, 4.5)  # Set limits based on battery voltage range
plt.xlim(0, Qbat)   # Set limits based on battery capacity
plt.show()
