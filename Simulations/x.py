import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

def Vol_t_Res(Dodbat):
    # Voltage model based on DOD
    Rbat_cell_diss = (-634.0 * Dodbat**10 + 2941 * Dodbat**9 - 5790.6 * Dodbat**8 +
                      6297.4 * Dodbat**7 - 4132.1 * Dodbat**6 + 1677.7 * Dodbat**5 -
                      416.4 * Dodbat**4 + 60.5 * Dodbat**3 - 4.8 * Dodbat**2 +
                      0.2 * Dodbat + 0)  # Dissipative resistance
    
    Vbat = (-8848 * Dodbat**10 + 40727 * Dodbat**9 - 79586 * Dodbat**8 +
             86018 * Dodbat**7 - 56135 * Dodbat**6 - 5565 * Dodbat**5 +
             784 * Dodbat**4 - 25 * Dodbat**3 + 55 * Dodbat**2 + 4)  # Voltage model

    return Vbat

def discharge_simulation(currents, total_time, cap_1h):
    time_steps = 500  # Number of steps in the discharge simulation
    capacities = np.linspace(0, cap_1h, time_steps)  # Create an array of capacities from 0 to 7 Ah
    results = {}

    for current in currents:
        voltages = []
        DOD = 0  # Initial Depth of Discharge

        for t in range(time_steps):
            # Update Depth of Discharge
            DOD = t * current / (cap_1h * (total_time / time_steps))
            if DOD > 1:
                DOD = 1  # Cap DOD to 1

            # Calculate the voltage based on the current DOD
            Vbat = Vol_t_Res(DOD)
            voltages.append(Vbat)

        results[current] = voltages  # Store voltage results for this current

    return capacities, results

# Parameters
cap_1h = 7  # 1-hour capacity in Ah
currents = [1.4, 3.5, 7, 14]  # Different currents for C/5, C/2, 1C, 2C discharge rates
total_time = 7  # Total discharge time in hours

# Run the discharge simulation
capacities, voltage_results = discharge_simulation(currents, total_time, cap_1h)

# Plotting
plt.figure(figsize=(10, 6))
for current, voltages in voltage_results.items():
    plt.plot(capacities[:len(voltages)], voltages, label=f'{current} A', marker='o')

# Additional plotting configurations
plt.xlabel('Capacity [Ah]')
plt.ylabel('Voltage [V]')
plt.title('Battery Voltage vs Capacity for Different Discharge Currents')
plt.legend()
plt.grid()
plt.xlim(0, cap_1h)
plt.ylim(0, 4.5)
plt.show()
