import numpy as np
import matplotlib.pyplot as plt

# Payload + Crew
num_pilot = 1 #DO NOT BETWEEN A/C
avg_wt_person = 200 #DO NOT BETWEEN A/C
total_wt_explosives = 18000

W_crew = num_pilot * avg_wt_person
W_payload = total_wt_explosives

print("W_crew:", W_crew, "lb")
print("W_payload:", W_payload, "lb")

# Fuel Fraction
L_D_max = 11  #CHANGE
L_D = 0.94 * L_D_max
c = 0.88 #DO NOT BETWEEN A/C
V = 500 #DO NOT BETWEEN A/C

W1_W0 = 0.970 #DO NOT BETWEEN A/C
W2_W1 = 0.930 #DO NOT BETWEEN A/C
W5_W4 = 0.995 #DO NOT BETWEEN A/C

R = 1200 #CHANGE
E = 20 / 60 #DO NOT BETWEEN A/C

W3_W2 = np.exp((-R * c) / (V * L_D))
W4_W3 = np.exp((-E * c) / (L_D))

W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
Wf_W0 = (1 - W5_W0) * 1.06

print("Fuel Fraction Wf/W0:", round(Wf_W0, 3))

# Engine Weight
def calculate_engine_weight(T_0):
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry / 1000)**1.078
    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start


# Empty Weight
def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage, TOGW, T_0, num_engines):
    W_wing = S_wing * 9
    W_ht = S_ht * 4
    W_vt = S_vt * 5.3
    W_fuselage = S_wet_fuselage * 4.8
    W_landing_gear = 0.045 * TOGW

    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3

    W_all_else = 0.17 * TOGW

    return W_wing + W_ht + W_vt + W_fuselage + W_landing_gear + W_engines + W_all_else


# Weight Fraction
def calculate_weight_fraction(R, E, c, V):
    L_D = 11 #CHANGE

    W1_W0 = 0.970 #DO NOT BETWEEN A/C
    W2_W1 = 0.930 #DO NOT BETWEEN A/C
    W5_W4 = 0.995 #DO NOT BETWEEN A/C

    W3_W2 = np.exp((-R * c) / (V * L_D))
    W4_W3 = np.exp((-E * c) / (L_D))

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    return (1 - W5_W0) * 1.06


# Inner Loop Weight Convergence
def inner_loop_weight(
    TOGW_guess,
    S_wing, S_ht, S_vt, S_wet_fuselage,
    num_engines, w_crew, w_payload, T_0,
    err=1e-6,
    max_iter=200
):
    delta = np.inf
    it = 0
    history = []

    while delta > err and it < max_iter:

        Wf_W0 = calculate_weight_fraction(R, E, c, V)
        W_fuel = Wf_W0 * TOGW_guess

        W_empty = calculate_empty_weight(
            S_wing, S_ht, S_vt, S_wet_fuselage,
            TOGW_guess, T_0, num_engines
        )

        W0_new = W_empty + w_crew + w_payload + W_fuel
        history.append(W0_new)

        delta = abs(W0_new - TOGW_guess) / max(abs(W0_new), 1e-9)
        TOGW_guess = W0_new
        it += 1

    return TOGW_guess, np.array(history)

# Outer Loop Thrust Convergence
def outer_loop_thrust(S_grid):

    # Aircraft constants
    e = 0.8 #DO NOT BETWEEN A/C
    AR = 2.7 #CHANGE
    CD_0 = 0.01 #CHANGE
    rho_sl = 0.00219 #DO NOT BETWEEN A/C
    rho_20k = 12.67e-4 #DO NOT BETWEEN A/C
    rho_30k = 10.66e-4 #DO NOT BETWEEN A/C

    g = 32.17

    k = 1 / (np.pi * e * AR)

    # Constraint Curves Store
    cruise_curve = []
    turn_curve = []
    dash_curve = []
    strike_curve = []
    climb_curve = []
    ceiling_curve = []
    governing_curve = []
    weight_curve = []

    for S_wing in S_grid:

        T_total = 40000 #CHANGE

        for _ in range(50):

            # Per-engine thrust
            T_0 = T_total

            # Converge weight
            W0, _ = inner_loop_weight(
                60000,
                S_wing, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_0
            )

            WS = W0 / S_wing

            W_to = W0
            T_to = 0.6 * W_to
            T_cr = 0.5 * T_to

            # Cruise Constraint
            W_cr = 0.9021 * W_to
            WS_cruise = (W_cr / W_to) * WS

            v_cruise = 0.8 * 900 # CHANGE
            q_cruise = 0.5 * rho_30k * v_cruise**2

            TW_cruise = (W_cr / W_to) / (T_cr / T_to) * (
                q_cruise * CD_0 / WS_cruise + (k / q_cruise) * WS_cruise
            )

            # Air to Air Combat Sustained Turn Constraint
            CLmax_la = 2.5 #CHANGE

            v_stall = np.sqrt((2/(rho_sl*CLmax_la))*W_to/S_wing)
            v_turn = 1.5 * v_stall

            turn_rate = 10 / 57.3
            n_turn = np.sqrt((turn_rate * v_turn / g)**2 + 1)

            q_turn = 0.5 * rho_20k * v_turn**2
            TW_turn = q_turn * CD_0 / WS + (k * n_turn**2 / q_turn) * WS

            # Air-to-Air Combat Dash Constraint
            v_dash = 2 * 900 #CHANGE
            q_dash = 0.5 * rho_30k * v_dash**2

            TW_atadash = (W_cr / W_to) / (T_cr / T_to) * (
                q_dash * CD_0 / WS_cruise + (k / q_dash) * WS_cruise
            )

            # Strike Dash Constraint
            v_strike = 0.9 * 1116
            q_strike = 0.5 * rho_sl * v_strike**2

            TW_strikedash = (W_cr / W_to) / (T_cr / T_to) * (
                q_strike * CD_0 / WS_cruise + (k / q_strike) * WS_cruise
            )

            # Climb Constraint
            k_s = 1.2
            CLmax_climb = 2 #CHNAGE
            climb_rate = 200 / 60

            TW_climb_uncorr = climb_rate/CLmax_climb*(CD_0/k)**(1/4)*(rho_sl/2)**(1/2)*(WS)**(-1/2)+2*(k*CD_0)**(1/2)
            TW_climb = (1/0.8) * TW_climb_uncorr

            # Ceiling Constraint
            TW_ceiling = 2 * np.sqrt(k * CD_0)

            TW_req = max(
                TW_cruise,
                TW_turn,
                TW_atadash,
                TW_strikedash,
                TW_climb,
                TW_ceiling,
            )

            T_req = TW_req * W0

            if abs(T_req - T_total) / T_total < 1e-4:
                break

            T_total = T_req

        cruise_curve.append(TW_cruise * W0)
        turn_curve.append(TW_turn * W0)
        dash_curve.append(TW_atadash * W0)
        strike_curve.append(TW_strikedash * W0)
        climb_curve.append(TW_climb * W0)
        ceiling_curve.append(TW_ceiling * W0)

        governing_curve.append(T_total)
        weight_curve.append(W0)

    return (np.array(cruise_curve),
            np.array(turn_curve),
            np.array(dash_curve),
            np.array(strike_curve),
            np.array(climb_curve),
            np.array(ceiling_curve),
            np.array(governing_curve),
            np.array(weight_curve))

def outer_loop_wing_area(T_grid):
    
    # Aircraft constants
    e = 0.8 # DO NOT BETWEEN A/C
    AR = 2.7 # CHANGE
    rho_sl = 0.00219 # DO NOT BETWEEN A/C

    g = 32.17

    k = 1 / (np.pi * e * AR)

    # Constraint Curves Store
    launch_curve = []
    recovery_curve = []
    governing_curve_T = []
    weight_curve_T = []
    instantturn_curve = []

    for T_total in T_grid:

        S_req = 500 

        for _ in range(50):

            S_0 = S_req

            # Converge weight
            W0, _ = inner_loop_weight(
                60000,
                S_0, S_ht, S_vt, S_wet_fuselage,
                num_engines, W_crew, W_payload, T_total
            )

            WS = W0 / S_0

            # Launch Constraint
            CLmax_la = 2.5 #CHANGE
            v_wod_launch = 0
            v_cat_launch = 165 * 1.688 # ft/s # Roskam, Part I, Eqn 3.10
            v_wod_recovery = 15 * 1.688 # ft/s # RFP
            CLmax_to = 1.8 # Takeoff
            WS_launch = (0.5*rho_sl*(v_wod_launch + v_cat_launch)**2*CLmax_to) / (1.21)
            S_launch = W0/WS_launch

            # Recovery Constraint
            v_stall = np.sqrt((2/(rho_sl*CLmax_la))*W0/S_req) # ft/s
            v_approach = 1.1 * v_stall # ft/s
            v_engage = 1.05 * v_approach
            W_to = W0
            W_la = 0.89 * W0
            WS_landing_recovery = 0.5*rho_sl*(v_engage+v_wod_recovery)**2*CLmax_la
            WS_recovery = W_to / W_la * WS_landing_recovery
            S_recovery = W0/WS_recovery

            # Air to Air Combat Instantaneous Turn Constraint
            CLmax_mn = 2.8 #CHANGE
            W_mn = 0.85 * W_to
            v_mn = 400 * 1.688 # ft/s
            q_mn = 0.5*rho_sl*v_mn**2
            n_max = 8
            WS_instantturn = q_mn*CLmax_mn/n_max*W_to/W_mn
            S_instantturn = W0/WS_instantturn

            WS_req = min(
                WS_launch,
                WS_recovery,
                WS_instantturn
            )

            S_req = 1/(WS_req)*W0

            if abs(S_req - S_0) / (S_0) < 1e-4:
                S_current = S_req
                break

            S_current = S_req

        launch_curve.append(S_launch)
        recovery_curve.append(S_recovery)
        instantturn_curve.append(S_instantturn)

        governing_curve_T.append(S_current)
        weight_curve_T.append(W0)

    return(np.array(launch_curve),
           np.array(recovery_curve),
           np.array(instantturn_curve),
           np.array(governing_curve_T),
           np.array(weight_curve_T))

# Plot Section
S_ht = 151 #CHANGE
S_vt = 24.5 #CHANGE
S_wet_fuselage = 693 #CHANGE 
num_engines = 1 #NO NOT BETWEEN A/C

S_grid = np.arange(200, 1200, 3)
T_grid = np.arange(10000, 200000, 100)

(cruise_curve,
 turn_curve,
 dash_curve,
 strike_curve,
 climb_curve,
 ceiling_curve,
 governing_curve,
 weight_curve) = outer_loop_thrust(S_grid)

(launch_curve,
 recovery_curve,
 instantturn_curve,
 governing_curve_T,
 weight_curve_T) = outer_loop_wing_area(T_grid)

# Shade feasible region
thrust_floor = np.maximum.reduce([
    cruise_curve, turn_curve, dash_curve, 
    strike_curve, climb_curve, ceiling_curve
])

instantturn_ceiling = np.interp(S_grid, instantturn_curve, T_grid)

plt.figure(figsize=(12, 7))

plt.plot(S_grid, cruise_curve, label="Cruise", linewidth=2)
plt.plot(S_grid, turn_curve, label="Air to Air Combat Sustained Turn", linewidth=2)
plt.plot(S_grid, dash_curve, label="Air to Air Combat Dash", linewidth=2)
plt.plot(S_grid, strike_curve, label="Strike Dash", linewidth=2)
plt.plot(S_grid, climb_curve, label="Climb", linewidth=2)
plt.plot(S_grid, ceiling_curve, label="Ceiling", linewidth=2)
plt.plot(launch_curve, T_grid, color='black', linestyle='--', linewidth=2, label="Launch")
plt.plot(recovery_curve, T_grid, color='red', linestyle='--', linewidth=2, label="Recovery")
plt.plot(instantturn_curve, T_grid, color ='green', linestyle ='--', linewidth=2, label = "Air to Air Combat Instantaneous Turn")

plt.plot(485, 41000, label = 'Design Point', marker = 'o')
plt.plot(500, 44000, label = 'F/A-18E/F Super Hornet', marker = 'o')
plt.plot(460, 40000, label = 'F-35 Lightning II', marker = 'o')

plt.fill_between(
    S_grid, 
    thrust_floor, 
    instantturn_ceiling, 
    where=(instantturn_ceiling > thrust_floor), 
    interpolate=True,
    color="grey", 
    alpha=0.3, 
    label="Feasible Region"
)

plt.xlim(400, 800)
plt.ylim(0, 140000)

plt.title("Converged T vs. S")
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Required Thrust (lbf)")
plt.grid(True)
plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.show()

# 1. Calculate weight specifically for your Design Point
S_design = 485 #DO NOT BETWEEN A/C
T_design = 44000 #DO NOT BETWEEN A/C

W0_design, _ = inner_loop_weight(
    60000, 
    S_design, S_ht, S_vt, S_wet_fuselage, 
    num_engines, W_crew, W_payload, T_design
)

We_design = calculate_empty_weight(
    S_design, S_ht, S_vt, S_wet_fuselage, 
    W0_design, T_design, num_engines
)

# Add these lines to your print block
print(f"Empty Weight (We): {We_design:,.2f} lb")
print(f"Empty Weight Fraction (We/W0): {We_design / W0_design:.3f}")
print(f"Fuel Weight (Wf): {W0_design - We_design - W_crew - W_payload:,.2f} lb")
print("-" * 30)

# Print the results
print("-" * 30)
print(f"DESIGN POINT RESULTS")
print(f"Wing Area (S): {S_design} ft²")
print(f"Total Thrust (T): {T_design} lbf")
print(f"Takeoff Gross Weight (W0): {W0_design:,.2f} lb")
print(f"Thrust-to-Weight Ratio (T/W): {T_design / W0_design:.3f}")
print(f"Wing Loading (W/S): {W0_design / S_design:.2f} lb/ft²")
print("-" * 30)