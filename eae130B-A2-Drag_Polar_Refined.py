import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ambiance import Atmosphere
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"

# Convert altitude
h_cruise_ft = 0
h_cruise_m = h_cruise_ft * 0.3048

# Initialize atmosphere
atm = Atmosphere(h_cruise_m)

# Extract properties (SI units)
rho = atm.density[0]
mu = atm.dynamic_viscosity[0]
T = atm.temperature[0]
P = atm.pressure[0]
a = atm.speed_of_sound[0]
print("Speed of Sound at Cruise: ", a)

# Cruise @ sea level
M_cruise = 0.85
V_cruise = M_cruise * a
q_cruise = 0.5 * rho * V_cruise**2

# Dash(M = 1.6 at 35,000 ft)
M_dash = 1.6
V_dash = M_dash * a
q_dash = 0.5 * rho * V_dash**2

# Aircraft Geometric Parameters
W_lb = 62473                                # lbs (MTOW)
W_kg = W_lb * 0.453592 # kg
b = 40                                      # Wingspan
b_flap = (0.637255 - 0.507317) * b          # Flap Span (from OpenVSP)
S_ref = 485                                 # ft^2 Reference Wing Area
S_ref_m2 = S_ref * 0.092903 # m^2
S_wet = 2401.143                            # ft^2 Wetted Surface Area of Aircraft
S_flap = (0.637255 - 0.507317) * S_ref      # ft^2 Flap Area
k = 1.33e-5                                 # Skin Roughness Value (Raymer Table 12.5)

d_fuselage = 5.46                           # ft Diameter of Fuselage

AR_clean = (b**2) / S_ref   # Aspect Ratio Clean Configuration
AR_flap = (b_flap**2) / S_flap   # Aspect Ratio Flap Deployment Configuration

e = 0.824 
e_TO = 0.775
e_landing = 0.725
K_clean = 1 / (np.pi * AR_clean * e) # Induced Drag Factor for Clean Configuration
K_TO = 1 / (np.pi * AR_clean * e_TO)
K_landing = 1 / (np.pi * AR_clean * e_landing)

# Estimating Zero-Lift Drag using Component Build-up Method (Cruise Conditions)
# Length of Aircraft Components [ft]
l_fuselage_c = 45.5 
l_wing_cbar = 16.45558             # Mean Aerodynamic Chord
l_HT_cbar = 9.50000                # Horizontal Stabilizer Chord
l_VT_cbar = 6.15266                # Vertical Stabilizer Chord
l_droptank = 17                    # Drop Tank

# Wetted Surface Area of Aircraft Components [ft^2]
S_wet_fuselage = 883.59
S_wet_wing = 485.43
S_wet_HT = 184.98
S_wet_VT = 120.5
S_wet_droptank = 15.95 # Drop Tank

# Cutoff Reynolds Number for Components
# Subsonic Flight
R_cutoff_fuselage = 38.21 * (l_fuselage_c / k) ** 1.053
R_cutoff_wing = 38.21 * (l_wing_cbar / k) ** 1.053
R_cutoff_HT = 38.21 * (l_HT_cbar / k) ** 1.053
R_cutoff_VT = 38.21 * (l_VT_cbar / k) ** 1.053
R_cutoff_droptank = 38.21 * (l_droptank / k) ** 1.053 

# Transonic or Supersonic (cd = cruise/dash)
R_cutoff_fuselage_cd = 44.62 * ((l_fuselage_c / k) ** 1.053) * (M_dash ** 1.16)
R_cutoff_wing_cd = 44.62 * ((l_wing_cbar / k) ** 1.053) * (M_dash ** 1.16)
R_cutoff_HT_cd = 44.62 * ((l_HT_cbar / k) ** 1.053) * (M_dash ** 1.16)
R_cutoff_VT_cd = 44.62 * ((l_VT_cbar / k) ** 1.053) * (M_dash ** 1.16)
R_cutoff_droptank_cd = 44.62 * (l_droptank / k) ** 1.053 * (M_dash ** 1.16)

# Laminar Skin Friction Coefficient for Components
C_fc_lam_fuselage = 1.328 / np.sqrt(R_cutoff_fuselage)
C_fc_lam_wing = 1.328 / np.sqrt(R_cutoff_wing)
C_fc_lam_HT = 1.328 / np.sqrt(R_cutoff_HT)
C_fc_lam_VT = 1.328 / np.sqrt(R_cutoff_VT)
C_fc_lam_droptank = 1.328 / np.sqrt(R_cutoff_droptank)

# Turbulent Skin Friction Coefficient for Components
#Cruise
C_fc_turb_fuselage_c = 0.455 / ((np.log10(R_cutoff_fuselage_cd) ** 2.58) * (1 + 0.144 * M_cruise**2) ** 0.65)
C_fc_turb_wing_c = 0.455 / ((np.log10(R_cutoff_wing_cd) ** 2.58) * (1 + 0.144 * M_cruise**2) ** 0.65)
C_fc_turb_HT_c = 0.455 / ((np.log10(R_cutoff_HT_cd) ** 2.58) * (1 + 0.144 * M_cruise**2) ** 0.65)
C_fc_turb_VT_c = 0.455 / ((np.log10(R_cutoff_VT_cd) ** 2.58) * (1 + 0.144 * M_cruise**2) ** 0.65)
C_fc_turb_droptank = 0.455 / ((np.log10(R_cutoff_droptank_cd) ** 2.58) * (1 + 0.144 * M_cruise**2) ** 0.65)

# Supersonic Dash
C_fc_turb_fuselage_d = 0.455 / ((np.log10(R_cutoff_fuselage_cd) ** 2.58) * (1 + 0.144 * M_dash**2) ** 0.65)
C_fc_turb_wing_d = 0.455 / ((np.log10(R_cutoff_wing_cd) ** 2.58) * (1 + 0.144 * M_dash**2) ** 0.65)
C_fc_turb_HT_d = 0.455 / ((np.log10(R_cutoff_HT_cd) ** 2.58) * (1 + 0.144 * M_dash**2) ** 0.65)
C_fc_turb_VT_d = 0.455 / ((np.log10(R_cutoff_VT_cd) ** 2.58) * (1 + 0.144 * M_dash**2) ** 0.65)
C_fc_turb_droptank = 0.455 / ((np.log10(R_cutoff_droptank_cd) ** 2.58) * (1 + 0.144 * M_dash**2) ** 0.65)


# Friction Drag Form Factor (FF) for Components
#Fuselage (FF)
f_fuselage = l_fuselage_c / d_fuselage # Fineness Ratio for Fuselage
FF_fuselage = (0.9 + (5 / (f_fuselage ** 3)) + (f_fuselage / 400)) # Form Factor for Fuselage (Raymer 12.31), use f>6

# Wing (FF)
tc_wing = 0.05 # Thickness-to-Chord Ratio for Wing (NACA 64-205)
A_wing = 40 # Sweep angle wing
FF_wing_cruise = (1 + (0.6/(0.25)*tc_wing) + 100*(tc_wing) ** 4) * ((1.34 * M_cruise**0.18) * (np.cos(np.radians(A_wing))**0.28)) #(Raymer 12.30) (Cruise Conditions)
FF_wing_dash = (1 + (0.6/(0.25)*tc_wing) + 100*(tc_wing) ** 4) * ((1.34 * M_dash**0.18) * (np.cos(np.radians(A_wing))**0.28)) #(Raymer 12.30) (Supersonic Conditions)

# Horizontal Tail (FF_HT)
tc_HT = 0.1 # Thickness-to-Chord Ratio for Horizontal Tail (can change to 0.06429)
A_HT = 38.07829 # Sweep angle HT
FF_HT_cruise = (1 + (0.6/(0.25)*tc_HT) + 100*(tc_HT) ** 4) * ((1.34 * M_cruise**0.18) * (np.cos(np.radians(A_HT))**0.28)) #(Raymer 12.30) (Cruise Conditions)
FF_HT_dash = (1 + (0.6/(0.25)*tc_HT) + 100*(tc_HT) ** 4) * ((1.34 * M_dash**0.18) * (np.cos(np.radians(A_HT))**0.28)) #(Raymer 12.30) (Supersonic Conditions)

# Vertical Tail (FF_VT)
tc_VT = 0.02000 # Thickness-to-Chord Ratio for Vertical Tail
A_VT = 28.46975 # Sweep angle VT
FF_VT_cruise = (1 + (0.6/(0.25)*tc_VT) + 100*(tc_VT) ** 4) * ((1.34 * M_cruise**0.18) * (np.cos(np.radians(A_VT))**0.28)) #(Raymer 12.30) (Cruise Conditions)
FF_VT_dash = (1 + (0.6/(0.25)*tc_VT) + 100*(tc_VT) ** 4) * ((1.34 * M_dash**0.18) * (np.cos(np.radians(A_VT))**0.28)) #(Raymer 12.30) (Supersonic Conditions)

# Component Drag Coefficients for Cruise Conditions
Q_Fuselage = 1.0 # Interference Factor for Fuselage
Q_wing = 1.05 # Interference Factor for Well-filleted Wing (Raymer Table 12.6))
Q_HT = 1.05 # Interference Factor for Horizontal Tail (Raymer Table 12.6)
Q_VT = 1.03 # Interference Factor for Clean V-Tail
Q_droptank = 1.5

# Multplying stuff
# Laminar
CD_fuselage_lam = (C_fc_lam_fuselage * FF_fuselage * Q_Fuselage * S_wet_fuselage)
CD_wing_lam = (C_fc_lam_wing * FF_wing_cruise * Q_wing * S_wet_wing)
CD_HT_lam = (C_fc_lam_HT * FF_HT_cruise * Q_HT * S_wet_HT)
CD_VT_lam = (C_fc_lam_VT * FF_VT_cruise * Q_VT * S_wet_VT)
CD_droptank_lam = (C_fc_lam_droptank * FF_wing_cruise * Q_droptank * S_wet_droptank)

# Turbulent
CD_fuselage_turb_c = (C_fc_turb_fuselage_c * FF_fuselage * Q_Fuselage * S_wet_fuselage)
CD_wing_turb_c = (C_fc_turb_wing_c * FF_wing_cruise * Q_wing * S_wet_wing)
CD_HT_turb_c = (C_fc_turb_HT_c * FF_HT_cruise * Q_HT * S_wet_HT)
CD_VT_turb_c = (C_fc_turb_VT_c * FF_VT_cruise * Q_VT * S_wet_VT)
CD_droptank_turb_c = (C_fc_turb_droptank * FF_wing_cruise * Q_droptank * S_wet_droptank)

#Supersonic, set Q = 1
CD_fuselage_turb_d = (C_fc_turb_fuselage_d * FF_fuselage * Q_Fuselage * S_wet_fuselage)
CD_wing_turb_d = (C_fc_turb_wing_d * FF_wing_dash * Q_Fuselage * S_wet_wing)
CD_HT_turb_d = (C_fc_turb_HT_d * FF_HT_dash * Q_Fuselage * S_wet_HT)
CD_VT_turb_d = (C_fc_turb_VT_d * FF_VT_dash * Q_Fuselage * S_wet_VT)
CD_droptank_turb_d = (C_fc_turb_droptank * FF_wing_dash * Q_Fuselage * S_wet_droptank)

# Miscellaneous Drag Coefficients
A_speedbrake = 12.5 # ft^2 Speed Brake Area (assumed/estimated)
D_q_speed_brake_subsonic = 0.139 + 0.419*((M_cruise-0.161)**2) * A_speedbrake # Fuselage-mounted Speed Brake Drag Area (Raymer 12.37)
D_q_speed_brake_supersonic = 0.064 + (0.4042*(M_dash - 3.84) ** 2) * A_speedbrake # Fuselage-mounted Speed Brake Drag Area at Supersonic Conditions (Raymer 12.38)

D_q_arresting_hook = 0.10 # Drag from Arresting Hook (Raymer 12.34)
CD_speedbrake = (1/S_ref) *  (1.0) * A_speedbrake # Speedbrake fueslage mounted
CD_arresting_hook = (1/S_ref) * D_q_arresting_hook
CD_strut = 3*(0.05)*(3.09 * 5)/S_ref # Strut
CD_main_wheel = 2 * (0.25) * (0.52 * 1.42) / S_ref # Main Gear
CD_nose_wheel = (0.25) * (2.92 * 0.958) / S_ref
CD_landing_gear =  CD_strut + CD_main_wheel + CD_nose_wheel # Wheel + Strut
print(CD_landing_gear)

# Traditionally, F/A-18 has 3 Flap Settings (AUTO, HALF, FULL) for the following conditions (Cruise, Takeoff, Landing) respectively.
# The following is the deflection angles associated with each flap configuration:
# AUTO = 0 - 17 degrees | HALF = ~ 30 degrees | FULL = ~ 45 degrees
# Estimating Flap Drag (Slotted Flaps)
F_flap = 0.0074 # Flap Form Factor (Slotted Flaps)
cf = 0.25 * l_wing_cbar # Flap Chord Length
CD_flap_auto = F_flap * (cf / l_wing_cbar) * (S_flap / S_ref) * (0 - 10) # Flap Drag Coefficient (Raymer 12.61)
CD_flap_half = 2 * F_flap * (cf / l_wing_cbar) * (S_flap / S_ref) * (30 - 10) # Flap Drag Coefficient (Raymer 12.61)
CD_flap_full = 2 * F_flap * (cf / l_wing_cbar) * (S_flap / S_ref) * (45 - 10) # Flap Drag Coefficient (Raymer 12.61)

# Estimated Total Aircraft Drag Polar (OpenVSP)
CD_wave_clean = 0.02 # OpenVSP Wave drag
CD_wave_dash = 0.0665 # Estimated Wave Drag at Supersonic Dash Conditions (Mach 1.6) (OpenVSP Wave Drag) -- aircraft simplified
CD0_lam = (1/S_ref) * (CD_fuselage_lam + CD_wing_lam + CD_HT_lam + CD_VT_lam + CD_droptank_lam) + CD_wave_clean   # Total Zero-Lift Drag Coefficient (CD0) for Cruise Conditions
CD0_turb_c = (1/S_ref) * (CD_fuselage_turb_c + CD_wing_turb_c + CD_HT_turb_c + CD_VT_turb_c + CD_droptank_turb_c) + CD_wave_clean # Total Zero-Lift Drag Coefficient (CD0) for Cruise Conditions (Turbulent Flow)
CD0_turb_d = (1/S_ref) * (CD_fuselage_turb_d + CD_wing_turb_d + CD_HT_turb_d + CD_VT_turb_d + CD_droptank_turb_d) + CD_wave_dash  # Total Zero-Lift Drag Coefficient (CD0) for Supersonic Dash Conditions (Turbulent Flow)

# Total CD of Aircraft for all 5 Configurations
CL_clean = np.linspace(-0.75, 1, num=100)
CL_TO = np.linspace(-1.5, 2, num=100)
CL_Landing = np.linspace(-1.9, 2.6, num=100)

CL_min_drag = W_kg / (q_cruise * S_ref_m2) # Lift Coefficient at Minimum Drag Condition
CL_min_drag = 0.2564

# Estimating Trim Drag (from OpenVSP)
CD_trim_clean = 0.001
CD_trim_TO = 0.0003
CD_trim_land = 0.0002

CD_LP = 0.10 # Estimated Leakage & Protuberance Drag (Raymer Table 12.8) -- 10% of parasite drag
df = pd.read_csv('/Users/dinoespineli/Documents/1 - My files/EAE130 - Senior Design/Clean_Processed.csv')

#CD_clean = (CD0_turb_c + CD_trim_clean)*(1+CD_LP) + df['CDi_clean'] #(K_clean*(CL_clean - CL_min_drag)**2)                     # Clean, Cruise
df['CD_total_clean'] = ((CD0_turb_c + CD_trim_clean) * (1 + CD_LP)) + df['CDi_clean']
df['CD_TO_GD'] = (CD0_turb_c + CD_trim_TO +  (CD_flap_half) + CD_landing_gear)*(1+CD_LP) + df['CDi_TO'] #(K_TO*(CL_TO - CL_min_drag)**2)          # Takeoff Flaps, Gear Down
df['CD_TO_GU'] = (CD0_turb_c + CD_trim_TO + (CD_flap_half))*(1+CD_LP) + df['CDi_TO'] #(K_TO*(CL_TO - CL_min_drag)**2)                         # Takeoff Flaps, Gear Up
df['CD_L_GD'] = (CD0_turb_c + CD_trim_land + (CD_flap_full) + CD_landing_gear + CD_arresting_hook + CD_speedbrake)*(1+CD_LP) +  df['CDi_land'] #(K_landing*(CL_Landing - CL_min_drag)**2)      # Landing Flaps, Gear Down
df['CD_L_GU'] = (CD0_turb_c + CD_trim_land + (CD_flap_full) + CD_arresting_hook + CD_speedbrake)*(1+CD_LP) + df['CDi_land'] #(K_landing*(CL_Landing - CL_min_drag)**2)     # Landing Flaps, Gear Up

# Printing minimum points

K_test = 1 / (np.pi * AR_clean * 16.33)
CDi_clean = (K_test*(CL_clean - CL_min_drag)**2) 
CDi_avg = np.mean(CDi_clean)
print("Average CDi (clean):", CDi_avg)

K_TO_test = 1 / (np.pi * AR_clean * 51.46)
CDi_to = (K_TO*(K_TO_test - CL_min_drag)**2)
CDi_avg_to = np.mean(CDi_to)
print("Average CDi (TO):", CDi_avg_to)

K_land_test = 1 / (np.pi * AR_clean * 54)
CDi_land = (K_land_test*(CL_Landing - CL_min_drag)**2) 
CDi_avg_to = np.mean(CDi_land)
print("Average CDi (TO):", CDi_avg_to)

# Plots
plt.plot(df['CD_total_clean'], df['Cli_clean'], label="Clean, Cruise")
plt.plot(df['CD_TO_GU'], df['Cli_TO'], label="Takeoff Flaps + Gear Up")
plt.plot(df['CD_TO_GD'], df['Cli_TO'], label="Takeoff Flaps + Gear Down")
plt.plot(df['CD_L_GU'], df['Cli_land'], label="Landing Flaps + Gear Up")
plt.plot(df['CD_L_GD'], df['Cli_land'], label="Landing Flaps + Gear Down")
plt.xlim(0,0.5)
plt.xticks(np.arange(0, 0.5, 0.05))
plt.yticks(np.arange(-2, 3.5, 0.5))
plt.ylim(-1,2)
plt.xlabel("$C_D$")
plt.ylabel("$C_L$")
plt.title("Drag Polar for Zephyr Nova 1")
plt.legend()
plt.grid(True)
plt.show() 

# Function to find CD when CL = 0
def find_CD_at_CL0(CL_array, CD_array, label):

    # Remove NaNs
    mask = ~np.isnan(CL_array) & ~np.isnan(CD_array)

    CL = np.array(CL_array[mask])
    CD = np.array(CD_array[mask])

    # Sort by CL
    sorted_idx = np.argsort(CL)

    CL_sorted = CL[sorted_idx]
    CD_sorted = CD[sorted_idx]

    # Interpolate
    CD_at_CL0 = np.interp(0, CL_sorted, CD_sorted)

    print(f"{label}: CD at CL = 0 --> {CD_at_CL0:.6f}")

    # Plot point
    plt.scatter(CD_at_CL0, 0, s=80)

    return CD_at_CL0

# Find zero-crossings
find_CD_at_CL0(df['Cli_clean'], df['CD_total_clean'], "Clean")

find_CD_at_CL0(df['Cli_TO'], df['CD_TO_GU'], "Takeoff Gear Up")

find_CD_at_CL0(df['Cli_TO'], df['CD_TO_GD'], "Takeoff Gear Down")

find_CD_at_CL0(df['Cli_land'], df['CD_L_GU'], "Landing Gear Up")

find_CD_at_CL0(df['Cli_land'], df['CD_L_GD'], "Landing Gear Down")

