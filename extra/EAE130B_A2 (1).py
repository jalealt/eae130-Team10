import numpy as np
import matplotlib.pyplot as plt

# Inputs
W_lb = 52200             
S_ref_ft2 = 485           
b_ft = 40                 
e = 0.824                
CD0_clean = 0.08144728538005883

# at 35,000 ft
rho = 0.38               
a = 295                   

# Conversion
W_kg = W_lb * 0.453592
S_ref_m2 = S_ref_ft2 * 0.092903
AR = b_ft**2 / S_ref_ft2
K_clean = 1 / (np.pi * AR * e)
M_cruise = 0.85
V_cruise = M_cruise * a
q_cruise = 0.5 * rho * V_cruise**2
CL_min_drag = W_kg / (q_cruise * S_ref_m2)

# Sweep
M = np.linspace(0.4, 2.0, 400)
V = M * a
q = 0.5 * rho * V**2
CL = W_kg / (q * S_ref_m2)

# CD
CD_base = CD0_clean + K_clean * (CL - CL_min_drag)**2
CD_peak = 0.014 * np.exp(-((M - 1.28) / 0.11)**2)
CD_plateau = 0.0045 / (1 + np.exp(-(M - 1.18) / 0.06))
CD = CD_base + CD_peak + CD_plateau

# Mach
M_req = np.array([0.85, 0.90, 1.60, 2.00])
CD_req = np.interp(M_req, M, CD)

# Plot
plt.figure(figsize=(11, 7))
plt.plot(M, CD, 'k', linewidth=2.5, label='Clean Configuration Drag Curve')

plt.plot(M_req[0], CD_req[0], 'o', color='red', markersize=10,
         label='Strike Dash Required (M = 0.85)')
plt.plot(M_req[1], CD_req[1], 'o', color='blue', markersize=10,
         label='Strike Dash Desired (M = 0.90)')
plt.plot(M_req[2], CD_req[2], 'o', color='green', markersize=10,
         label='Air-to-Air Dash Required (M = 1.6)')
plt.plot(M_req[3], CD_req[3], 'o', color='magenta', markersize=10,
         label='Air-to-Air Dash Desired (M = 2.0)')
plt.xlim(0.4, 2.05)
plt.xlabel('Mach Number (M)', fontsize=16)
plt.ylabel('Drag Coefficient ($C_D$)', fontsize=16)
plt.title('Clean Configuration Drag Estimate vs. Mach Number', fontsize=18)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=11)
plt.show()