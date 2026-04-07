import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Constants
W_to = 70000 # lbs #CHANGE
W_la = 0.89 * W_to # lbs
W_cr = 0.9021 * W_to # lbs
W_mn = 0.85 * W_to # lbs

T_to = 0.6 * W_to # Raymer pg. 117
T_cr = 0.5 * T_to # Raymer pg. 122

S_ref = 450 # ft^2 #CHANGE
S_wet = 2600 # ft^2 #CHANGE

CD_0 = 0.008 #CHANGE
e = 0.85
AR = 3.2 #CHANGE
n = 8

#CHANGE ALL
CLmax_to = 2.4 # Takeoff
CLmax_la = 2.5 # Landing
CLmax_clean = 1.6
CLmax_climb = 2.5
CLmax_mn = 2.8

rho_sl = 0.00219 # slug/ft^3 # Raymer pg. 131
rho_10k = 17.56*10**-4 # slug/ft^3
rho_20k = 12.67*10**-4 # slug/ft^3
rho_30k = 10.66*10**-4 # slug/ft^3 
v_stall = np.sqrt((2/(rho_sl*CLmax_la))*W_to/S_ref) # ft/s
v_approach = 1.1 * v_stall # ft/s
v_engage = 1.05 * v_approach

v_wod_launch = 0
v_cat_launch = 165 * 1.688 # ft/s # Roskam, Part I, Eqn 3.10
v_wod_recovery = 15 * 1.688 # ft/s # RFP
v_turn = 1.4*v_stall # ft/s
turn_rate = 7 / 57.3 # rad/s
g = 32.17 # ft/s^2

k_s = 1.2
v_climb = k_s * v_stall # Roskam pg. 996 Table F.2
climb_rate = 200/60 # ft/s
G = climb_rate/v_climb
k = 1/(np.pi*e*AR)

WS = np.linspace(1,300,300)

# Launch Constraint
WS_launch = (0.5*rho_sl*(v_wod_launch + v_cat_launch)**2*CLmax_to) / (1.21) * np.ones (300)

# Recovery Constraint
WS_landing_recovery = 0.5*rho_sl*(v_engage+v_wod_recovery)**2*CLmax_la
WS_recovery = W_to / W_la * WS_landing_recovery * np.ones(300)

# Air to Air Combat Instantaneous Turn Constraint
v_mn = 400 * 1.688 # ft/s
q_mn = 0.5*rho_sl*v_mn**2
n_max = 8
WS_mn = q_mn*CLmax_mn/n_max*W_to/W_mn * np.ones(300)

# Air to Air Combat Sustained Turn Constraint
# Assume aircraft is flying at 1.5x SL stall speed at 20k ft
n_turn = np.sqrt((turn_rate*v_turn/g)**2+1)
q_turn = 0.5*rho_20k*(v_turn)**2
TW_turn = q_turn*CD_0/WS + 0.85*(k*n_turn**2/q_turn)*WS

# Air to Air Combat Dash Constraint
# Aircraft is flying at Mach 2.0 at 30k ft according to RFP
WS_cruise = (W_cr/W_to)*WS
M_atadash = 2
v_atadash = 2*993 # ft/s
q_atadash = 0.5*rho_30k*(v_atadash)**2
TW_cruise_atadash = q_atadash*CD_0/WS_cruise + (k/q_atadash)*WS_cruise
TW_atadash = (W_cr/W_to)/(T_cr/T_to)*TW_cruise_atadash

# Strike Dash Constraint
# Aircraft is flying at Mach 0.9 at SL according to RFP
M_strikedash = 0.9
v_strikedash = 0.9*1116 # ft/s
q_strikedash = 0.5*rho_sl*(v_strikedash)**2
TW_cruise_strikedash = q_strikedash*CD_0/WS_cruise + (k/q_strikedash)*WS_cruise
TW_strikedash = (W_cr/W_to)/(T_cr/T_to)*TW_cruise_strikedash

# Climb Constraint
# TW_climb_uncorr = (k_s**2+CD_0)/CLmax_climb + k*CLmax_climb/k_s**2 + G
TW_climb_uncorr = climb_rate/CLmax_climb*(CD_0/k)**(1/4)*(rho_sl/2)**(1/2)*(WS)**(-1/2)+2*(k*CD_0)**(1/2)
TW_climb = (1/0.8) * TW_climb_uncorr

# Ceiling Constraint
TW_ceiling = 2*np.sqrt(k*CD_0) * np.ones(300)

# Cruise Constraint
# Assume aircraft is flying at Mach 0.8 at 30k ft
M_cruise = 0.8
v_cruise = 0.8*993 # ft/s
q_cruise = 0.5*rho_30k*(v_cruise)**2
TW_cruise_uncorr = q_cruise*CD_0/WS_cruise + k/q_cruise*WS_cruise
TW_cruise = (W_cr/W_to)/(T_cr/T_to)*TW_cruise_uncorr

# Create Plot
plt.figure(figsize=(8,4))
plt.title('T/W vs. W/S for F-35')
plt.xlabel("W/S $(lb/ft^2)$")
plt.ylabel("T/W")

plt.plot(WS_launch, np.linspace(0,3,300), label = 'Launch', linestyle = '-', linewidth = 2)
plt.plot(WS_recovery, np.linspace(0,30,300), label = 'Recovery', linestyle = '-', linewidth = 2)
plt.plot(WS_mn, np.linspace(0,30,300), label = 'Air to Air Combat Instantaneous Turn', linestyle = '-', linewidth = 2)
plt.plot(WS, TW_turn, label = 'Air to Air Combat Sustained Turn', linestyle = '-', linewidth =2)
plt.plot(WS, TW_atadash, label = 'Air to Air Combat Dash', linestyle = '-', linewidth =2)
plt.plot(WS, TW_strikedash, label = 'Strike Dash', linestyle = '-', linewidth =2)
plt.plot(WS, TW_ceiling, label = 'Ceiling', linestyle = '-', linewidth =2)
plt.plot(WS, TW_climb, label = 'Climb', linestyle = '-', linewidth =2)
plt.plot(WS, TW_cruise, label = 'Cruise', linestyle = '-', linewidth =2)

plt.plot(152.17, 0.61, label = 'F-35', marker = 'o')

# Shade feasible region
feasible = WS <= WS_launch
min_TW = np.maximum.reduce([
    TW_turn,
    TW_atadash
])
plt.fill_between (
    WS[feasible],
    min_TW[feasible],
    3,
    alpha = 0.25,
    color = "grey",
    label = "Feasible Region"
)

plt.ylim(0, 3)
plt.legend(loc='best')
plt.show()