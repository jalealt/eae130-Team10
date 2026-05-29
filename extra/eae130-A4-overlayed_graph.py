import numpy as np
import matplotlib.pyplot as plt

def calculate_engine_weight(T_0):
    W_eng_dry = 0.521 * T_0**0.9
    W_eng_oil = 0.082 * T_0**0.65
    W_eng_rev = 0.034 * T_0
    W_eng_control = 0.26 * T_0**0.5
    W_eng_start = 9.33 * (W_eng_dry / 1000)**1.078
    return W_eng_dry + W_eng_oil + W_eng_rev + W_eng_control + W_eng_start


def calculate_empty_weight(S_wing, S_ht, S_vt, S_wet_fuselage,
                           TOGW, T_0, num_engines):

    W_wing = S_wing * 9
    W_ht = S_ht * 4
    W_vt = S_vt * 5.3
    W_fuselage = S_wet_fuselage * 4.8
    W_landing_gear = 0.045 * TOGW

    Engine_weight = calculate_engine_weight(T_0)
    W_engines = Engine_weight * num_engines * 1.3

    W_all_else = 0.17 * TOGW

    return (W_wing + W_ht + W_vt +
            W_fuselage + W_landing_gear +
            W_engines + W_all_else)


def calculate_weight_fraction(R, E, c, V, L_D_max):

    L_D = 0.94 * L_D_max

    W1_W0 = 0.970
    W2_W1 = 0.930
    W5_W4 = 0.995

    W3_W2 = np.exp((-R * c) / (V * L_D))
    W4_W3 = np.exp((-E * c) / (L_D))

    W5_W0 = W5_W4 * W4_W3 * W3_W2 * W2_W1 * W1_W0
    return (1 - W5_W0) * 1.06


def inner_loop_weight(TOGW_guess,
                      S_wing, S_ht, S_vt, S_wet_fuselage,
                      num_engines, W_crew, W_payload,
                      T_0, R, E, c, V, L_D_max):

    for _ in range(200):

        Wf_W0 = calculate_weight_fraction(R, E, c, V, L_D_max)
        W_fuel = Wf_W0 * TOGW_guess

        W_empty = calculate_empty_weight(
            S_wing, S_ht, S_vt, S_wet_fuselage,
            TOGW_guess, T_0, num_engines
        )

        W0_new = W_empty + W_crew + W_payload + W_fuel

        if abs(W0_new - TOGW_guess)/W0_new < 1e-6:
            break

        TOGW_guess = W0_new

    return W0_new

def outer_loop_thrust(S_grid, aircraft):

    e = aircraft["e"]
    AR = aircraft["AR"]
    CD_0 = aircraft["CD_0"]
    rho_sl = 0.00219
    rho_20k = 12.67e-4
    rho_30k = 10.66e-4
    g = 32.17

    k = 1 / (np.pi * e * AR)

    curves = [[] for _ in range(7)]
    weight_curve = []

    for S_wing in S_grid:

        T_total = 44000

        for _ in range(50):
            T_0 = T_total /aircraft["num_engines"]

            W0 = inner_loop_weight(
                60000,
                S_wing,
                aircraft["S_ht"],
                aircraft["S_vt"],
                aircraft["S_wet_fuselage"],
                aircraft["num_engines"],
                aircraft["W_crew"],
                aircraft["W_payload"],
                T_0,
                aircraft["R"],
                aircraft["E"],
                aircraft["c"],
                aircraft["V"],
                aircraft["L_D_max"]
            )

            WS = W0 / S_wing
            W_to = W0
            T_to = 0.6 * W_to
            T_cr = 0.5 * T_to
            W_cr = 0.9021 * W_to
            WS_cruise = (W_cr / W_to) * WS

            v_cruise = 0.8 * 993
            q_cruise = 0.5 * rho_30k * v_cruise**2
            TW_cruise = (W_cr/W_to)/(T_cr/T_to)*(
                q_cruise*CD_0/WS_cruise +
                (k/q_cruise)*WS_cruise)

            CLmax_la = 2.4
            v_stall = np.sqrt((2/(rho_sl*CLmax_la))*W_to/S_wing)
            v_turn = 1.5 * v_stall
            turn_rate = 10/57.3
            n_turn = np.sqrt((turn_rate*v_turn/g)**2 + 1)
            q_turn = 0.5*rho_20k*v_turn**2
            TW_turn = q_turn*CD_0/WS + (k*n_turn**2/q_turn)*WS

            v_dash = 2*993
            q_dash = 0.5*rho_30k*v_dash**2
            TW_dash = (W_cr/W_to)/(T_cr/T_to)*(
                q_dash*CD_0/WS_cruise +
                (k/q_dash)*WS_cruise)

            v_strike = 0.9*1116
            q_strike = 0.5*rho_sl*v_strike**2
            TW_strike = (W_cr/W_to)/(T_cr/T_to)*(
                q_strike*CD_0/WS_cruise +
                (k/q_strike)*WS_cruise)

            climb_rate = 200/60
            CLmax_climb = 1.8
            TW_climb = (1/0.8)*(climb_rate/CLmax_climb*
                       (CD_0/k)**0.25*(rho_sl/2)**0.5*
                       WS**(-0.5)+2*(k*CD_0)**0.5)

            TW_ceiling = 2*np.sqrt(k*CD_0)

            TW_req = max(TW_cruise, TW_turn, TW_dash,
                         TW_strike, TW_climb, TW_ceiling)

            T_req = TW_req * W0

            if abs(T_req - T_total)/T_total < 1e-4:
                break

            T_total = T_req

        curves[0].append(TW_cruise*W0)
        curves[1].append(TW_turn*W0)
        curves[2].append(TW_dash*W0)
        curves[3].append(TW_strike*W0)
        curves[4].append(TW_climb*W0)
        curves[5].append(TW_ceiling*W0)
        curves[6].append(T_total)
        weight_curve.append(W0)

    return [np.array(c) for c in curves], np.array(weight_curve)

W_crew = 200
W_payload = 10000

team_aircraft = {
    "L_D_max": 21.5, "c": 0.88, "V": 500,
    "R": 1000, "E": 20/60,
    "AR": 3.548, "CD_0": 0.01136, "e": 0.8,
    "S_ht": 173.50, "S_vt": 135.86,
    "S_wet_fuselage": 670.82,
    "num_engines": 1,
    "W_crew": W_crew,
    "W_payload": W_payload
}

comparable_aircraft = {
    "L_D_max": 20.5, "c": 0.88, "V": 835,
    "R": 1275, "E": 20/60,
    "AR": 4, "CD_0": 0.02, "e": 0.8,
    "S_ht": 101.2, "S_vt": 141.44,
    "S_wet_fuselage": 670.82,
    "num_engines": 2,
    "W_crew": W_crew,
    "W_payload": W_payload
}

S_grid = np.arange(400,1500,5)

team_curves, team_weight = outer_loop_thrust(S_grid, team_aircraft)
comp_curves, comp_weight = outer_loop_thrust(S_grid, comparable_aircraft)

team_WS = team_weight / S_grid
comp_WS = comp_weight / S_grid

# Design point detection
team_idx = np.where(team_WS <= 110)[0][0]
comp_idx = np.where(comp_WS <= 110)[0][0]

print("\nTEAM DESIGN POINT")
print("Wing Area:", S_grid[team_idx])
print("Weight:", round(team_weight[team_idx]))
print("Thrust:", round(team_curves[6][team_idx]))
print("W/S:", round(team_WS[team_idx],1))

print("\nCOMPARABLE DESIGN POINT")
print("Wing Area:", S_grid[comp_idx])
print("Weight:", round(comp_weight[comp_idx]))
print("Thrust:", round(comp_curves[6][comp_idx]))
print("W/S:", round(comp_WS[comp_idx],1))



plt.figure(figsize=(14,9))

constraint_names = ["Cruise","Turn","Dash",
                    "Strike","Climb","Ceiling","Governing"]

for i, name in enumerate(constraint_names):

    lw = 3 if name == "Governing" else 2

    color = f"C{i}"

    # Team (solid) 
    plt.plot(S_grid,
             team_curves[i],
             color=color,
             linewidth=lw,
             linestyle='-')

    # Comparable (dashed) 
    plt.plot(S_grid,
             comp_curves[i],
             color=color,
             linewidth=lw,
             linestyle='--')



plt.plot(S_grid[team_idx],
         team_curves[6][team_idx],
         marker='o',
         markersize=10,
         color='black',
         linestyle='None')

plt.plot(S_grid[comp_idx],
         comp_curves[6][comp_idx],
         marker='s',
         markersize=10,
         color='black',
         linestyle='None')


from matplotlib.lines import Line2D

legend_elements = []

# Constraint colors
for i, name in enumerate(constraint_names):
    lw = 3 if name == "Governing" else 2
    legend_elements.append(
        Line2D([0], [0],
               color=f"C{i}",
               lw=lw,
               label=name)
    )

# Aircraft styles
legend_elements.append(
    Line2D([0], [0], color='black',
           lw=2, linestyle='-',
           label='Team Aircraft')
)

legend_elements.append(
    Line2D([0], [0], color='black',
           lw=2, linestyle='--',
           label='Comparable Aircraft')
)

legend_elements.append(
    Line2D([0], [0],
           marker='o',
           color='black',
           linestyle='None',
           markersize=8,
           label='Design Point - Team')
)

legend_elements.append(
    Line2D([0], [0],
           marker='s',
           color='black',
           linestyle='None',
           markersize=8,
           label='Design Point - Comparable')
)

plt.legend(handles=legend_elements,
           loc="center left",
           bbox_to_anchor=(1, 0.5))

plt.title("Constraint Comparison\nTeam vs Comparable Aircraft")
plt.xlabel("Wing Area S (ft²)")
plt.ylabel("Required Thrust (lbf)")
plt.grid(True)
plt.tight_layout()
plt.show()