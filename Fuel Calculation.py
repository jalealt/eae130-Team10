import math
import numpy as np
import os
import matplotlib.pyplot as plt
os.system('cls')

S_ref = 485 #ft^2
C_D_0 = 0.01136
AR = 3
e = 0.8
k = 1 / (math.pi * AR * e)

R = 1000 #nm combat radius



W0 = 63000 #Start Guess Weight
c_dry = 0.886 #lbm/hr/lbf
T_dry = 28000 #lbf
c_wet = 1.920 #lbm/hr/lbf
T_wet = 43000 #lbf

W0_1 = (1 - (15/60) * c_dry/2 * (0.05 * T_dry / W0)) * W0 #Start, Warm-up, Taxi
W1 = (1 - (1/60) * c_wet * (T_wet / W0_1)) * W0_1 #Takeoff

#Solve Climb
final_altitude = 30000 #ft
rho = 0.0012
num_segments = 10
Delta_h = final_altitude/num_segments
climb_segments = np.linspace(0,final_altitude,num_segments+1)

W_climb = np.zeros(num_segments)
W_climb[0] = W1
V_climb = np.zeros(num_segments)
h_e_climb = np.zeros(num_segments)

#for i in range(0,num_segments):
    #V_climb[i] = math.sqrt((W_climb[i]/S_ref) / (3 * rho * C_D_0) * ((T_wet/W_climb[i]) + math.sqrt((T_wet/W_climb[i])**2 + 12 * C_D_0 * k)))
    #h_e_climb[i] = climb_segments[i] + V_climb[i]**2 / (2 * 32.2)
    #Delta_h_e = h_e_climb[i]
W2 = 0.94 * W1

#SOLVE CRUISE
V = 600 #knots cruise speed
L_D_cruise = 1.4

cruise_segments = 10
Delta_R = R / cruise_segments
W_cruise = np.zeros(cruise_segments)
W_cruise[0] = W2
R_cruise = np.linspace(0, R, cruise_segments)

for i in range(0, cruise_segments-1):
    C_l = 2 * W_cruise[i] / (rho * V**2 * S_ref)
    L_D = C_l / (C_D_0 + k * C_l**2)
    W_cruise[i+1] = W_cruise[i] * math.exp(-Delta_R * c_dry / (V * (L_D)))

plt.plot(R_cruise, W_cruise, color='blue', marker='o')
#plt.show()

W3 = W_cruise[-1]
W4 = 0.93 * W3
W5 = 0.992 * W4
W6 = 0.992 * W5

Empty_Weight = 41785 #lbf
Burned_Fuel = round(W0 - W6)
Total_Fuel = round(Burned_Fuel * 1.245)


print("Empty Weight: " + str(Empty_Weight) + " lb")
print("Total Fuel Weight: " + str(Total_Fuel) + " lb")
print("Weight of Burned Fuel: " + str(Burned_Fuel) + " lb")
print("Fuel Remaining: " + str(Total_Fuel - Burned_Fuel) + " lb")
print("Total Fuel Fraction: " + str(round(W6/W0,2)))
print("Full Weight: " + str(Empty_Weight + Total_Fuel) + " lb")
print("Initial Guess: " + str(W0) + " lb")

print("Weight Fractions")
print("W1/W0: " + str(round(W1/W0,2)) + " (Start, Warm-up, Taxi to Takeoff)")
print("W2/W1: " + str(round(W2/W1,2)) + " (Takeoff to Climb)")
print("W3/W2: " + str(round(W3/W2,2)) + " (Climb to Cruise)")
print("W4/W3: " + str(round(W4/W3,2)) + " (Cruise to Loiter)")
print("W5/W4: " + str(round(W5/W4,2)) + " (Loiter to Descend)")
print("W6/W5: " + str(round(W6/W5,2)) + " (Descend to Landing)")
print("W6/W0: " + str(round(W6/W0,2)) + " (Total fraction)")
