import math
import numpy as np

## Part 1: Preliminary Empennage Sizing (Vertical/Horizontal Tail)

# Empennage sizing

# Given values related to Vertical Tail #
S_vt = 174.91     # vertical tail area (ft^2) 
L_vt = 7.65      # vertical tail moment arm (ft) 

# Given values related to Wing #
b_w  = 43.4       # wing span tip-to-tip (ft) 
c_w  = 13.43001   # wing chord (ft) 
S_w  = 692.08     # wing area (ft^2) 

# Given values related to Horizontal Tail 
S_ht = 239.26     # horizontal tail area (ft^2) 
L_ht = 9.79       # horizontal tail moment arm (ft) 

# Solve for Tail Volume Coefficients #
c_vt = (S_vt * L_vt) / (b_w * S_w)  # Vertical Tail Volume Coefficient
c_ht = (S_ht * L_ht) / (c_w * S_w)  # Horizontal Tail Volume Coefficient

print("Estimated Vertical Tail Volume Coefficient = {} ".format(c_vt))
print("Estimated Horizontal Tail Volume Coefficient = {} ".format(c_ht))



## Part 2:Longitudinal Stability (Static Margin Estimation)

# 1. Find the lift slope curve of the main wing and of the horizontal tail.
AR_w  = 3.39868               # Aspect ratio of wing 
lambda_w = math.radians(30)   # Sweep angle of wing (radians) 

AR_h  = 2.00176                # Aspect ratio of horizontal stabilizer 
lambda_h = math.radians(33.17) # Sweep angle of horizontal stabilizer (radians) 

eta_w = 0.97   # Difference factor between the theoretical section lift curve slope for the wing 
eta_h = 0.90   # Difference factor between the theoretical section lift curve slope for the horizontal tail 

M     = 0.87 # Mach number 

CL_a_w  = (2*np.pi*AR_w)/(((2)+(np.sqrt((((AR_w/eta_w)**2)*(1+(np.tan(lambda_w))**2-M**2))+(4))))) # Lift curve slope of wing, / radian
CL_a_h0 = (2*np.pi*AR_h)/(((2)+(np.sqrt((((AR_h/eta_h)**2)*(1+(np.tan(lambda_h))**2-M**2))+(4))))) # Lift curve slope of horizantle tail, / radian

print("Lift curve slope of wing = {} / radian".format(CL_a_w))
print("Lift curve slope of horizontal tail = {} / radian".format(CL_a_h0))

# 2. Calculate the downwash
de_dalpha = 2*CL_a_w / (np.pi * AR_w)
print("Downwash: %.3f / radian" %de_dalpha)

CL_a_h = CL_a_h0 / (1 - de_dalpha)
print("Lift curve slope of horizontal tail corrected for downwash = {} / radian".format(CL_a_h))

# 3. Account for the contribution from the fuselage using the empirically-based method
Kf  = 0.344          # Empirical factor (Assumed) 
Lf  = 45.5           # Fuselage length (ft) 
Wf  = 8.66763        # Maximum width of fuselage (ft) 

dCmf_dCL = (Kf * (Wf ** 2) * Lf) / (S_w * c_w * CL_a_w)
print("dCmf_dCL = {}".format(dCmf_dCL))

# 4. Calculate the Static Margin
x_cg = 29.628         # Aircraft center of gravity (ft) assumed 
x_25MAC = 14.73       # Distance from nose to 25% MAC (ft) assumed 

SM = (x_cg-x_25MAC) / (c_w) - (CL_a_h * S_ht * L_ht) / (CL_a_w * S_w * c_w) + dCmf_dCL
print("SM = {}".format(-SM))