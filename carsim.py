# carsim 0.2
# Eric Straub

import matplotlib.pyplot as plt
import numpy as np
import threading
import json
import concurrent.futures
from time import sleep
from scipy.interpolate import interp1d



def simulate_quarter_mile(car):
    # Constants
    rho = 1.225             # air density in kg/m³
    g = 9.81                # gravity in m/s²
    quarter_mile = 402.336  # distance in meters
    delta_t = 0.01          # time increment in seconds
    drivetrain_power_loss = 0
    # drivetrain_power_loss = 0.15
    
    # Extract car parameters
    W = car["W"]
    P = car["P"]
    Cd = car["Cd"]
    A = car["A"]
    Crr = car["Crr"]
    Ft = calc_Ft(car)
    P_wheel = P * (1 - drivetrain_power_loss) # power at the wheels in watts
    gear_ratios = car["gear_ratios"]

    # Initial conditions
    v = 0   # initial velocity in m/s
    d = 0   # initial distance in meters
    t = 0   # initial time in seconds
    zerosixty_recorded = False
    current_gear = 1

    # Lists to store data for plotting
    time_data = []
    acceleration_data = []
    velocity_data = []
    distance_data = []
    power_data = []
    rpm_data = []

    # Simulation
    while d < quarter_mile:
        rpms = calc_rpm(v, gear_ratios[current_gear - 1], car["final_drive"], car["tire_diameter"])
        rpm = rpms[0]
        wheel_rpm = rpms[1]

        if rpm < 2500 and current_gear == 1: # Launch control
            rpm = 2500

        if rpm > car["redline"] - 300: # Shift up
            current_gear += 1
            continue

        power = calc_power(car, rpm)

        P_wheel = power * (1 - drivetrain_power_loss)


        Fe = P_wheel / v if v > 0.01 else P_wheel / 0.01      # engine force in N
        Fd = 0.5 * Cd * A * rho * v**2                  # drag force in N
        Fr = Crr * W * g                                # rolling resistance force in N
        Fn = Fe - Fd - Fr                               # net force in N

        if Fn > Ft:
            Fn = Ft

        a = Fn / W          # acceleration in m/s²
        v += a * delta_t    # velocity in m/s
        d += v * delta_t    # distance in meters
        t += delta_t        # time in seconds

        # Record data
        time_data.append(t)
        acceleration_data.append(a)
        velocity_data.append(v)
        distance_data.append(d)
        power_data.append(P_wheel)
        rpm_data.append(rpm)

        if not zerosixty_recorded and v > mph_to_ms(60):
            zerosixty = t
            zerosixty_recorded = True

        # # Print realtime data
        # if t % 0.1 < delta_t:
        #     print(f"{t:.2f} s, {v:.2f} m/s, {d:.2f} m", end="\r")
        #     sleep(0.1)

        # # Print realtime data with newline
        # if t % 0.1 < delta_t:
        #     print(f"{P_wheel:.2f} W, gear: {current_gear}, {rpm:.2f} rpm, {wheel_rpm:.2f} wheel rpm")
        #     sleep(0.1)

    if not zerosixty_recorded:
        zerosixty = t    
    
    data = {
        "quarter_time": t,
        "quarter_speed": v,
        "0-60 mph": zerosixty,
        "time_data": time_data,
        "acceleration_data": acceleration_data,
        "velocity_data": velocity_data,
        "distance_data": distance_data,
        "power_data": power_data,
        "rpm_data": rpm_data
    }

    return data


# Helper functions

def calc_Ft(car):
    return (car["mu"] * car["W"] * 9.81) * (car["Driven Wheels"] / car["Wheels"])

def calc_rpm(v, gear_ratio, final_drive, tire_diameter):
    wheel_rpm = v / (tire_diameter * np.pi)
    engine_rpm = wheel_rpm * gear_ratio * final_drive

    return [engine_rpm, wheel_rpm]

def calc_top_speed(car):
    gear_ratios = car["gear_ratios"]
    final_drive = car["final_drive"]
    tire_diameter = car["tire_diameter"]
    redline = car["redline"]

    speeds = []

    for gear in gear_ratios:
        wheel_rpm = redline / gear / final_drive
        speed = wheel_rpm * tire_diameter * np.pi
        speeds.append(speed)

    return speeds

def calc_power(car, rpm):
    torque_curve = car["torque_curve"]
    torque_curve_rpm = [x[0] for x in torque_curve]
    torque_curve_nm = [x[1] for x in torque_curve]

    torque_interp = interp1d(torque_curve_rpm, torque_curve_nm, kind='cubic')
    torque = torque_interp(rpm)
    power = torque * rpm * 2 * np.pi / 60

    return power

# Print and graph data
def graph_and_print(car, sim_data):
    print_car_info(car)
    print_simulation_info(sim_data)

    # Grab and convert units of lists
    acceleration_data_g = [ms2_to_g(a) for a in sim_data['acceleration_data']]
    velocity_data_mph = [ms_to_mph(v) for v in sim_data['velocity_data']]
    distance_data_ft = [d * 3.28084 for d in sim_data['distance_data']]
    power_data_hp = [watt_to_hp(p) for p in sim_data['power_data']]
    rpm_data = sim_data['rpm_data']
    time_data = sim_data['time_data']


    # Plotting the data
    # plt.figure(figsize=(12, 8))
    plt.figure(figsize=(12, 8))

    # Plot acceleration
    plt.subplot(3, 1, 1)
    plt.plot(time_data, acceleration_data_g, label='Acceleration (g)')
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (g)')
    plt.legend()

    # # Plot velocity
    # plt.subplot(5, 1, 2)
    # plt.plot(time_data, velocity_data_mph, label='Velocity (mph)', color='orange')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Velocity (mph)')
    # plt.legend()

    # # Plot distance
    # plt.subplot(5, 1, 3)
    # plt.plot(time_data, distance_data_ft, label='Distance (ft)', color='green')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Distance (ft)')
    # plt.legend()

    # Plot power
    plt.subplot(3, 1, 2)
    plt.plot(time_data, power_data_hp, label='Power (HP)', color='green')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (HP)')
    plt.legend()

    # Plot rpm
    plt.subplot(3, 1, 3)
    plt.plot(time_data, rpm_data, label='RPM', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('RPM')
    plt.legend()

    plt.tight_layout()
    plt.show()


def print_car_info(car):
    print(f"Car:\t\t\t{car['Year']} {car['Name']}")
    print(f"Weight:\t\t\t{kg_to_lb(car['W']):.2f} lb,\t{car['W']:.2f} kg")
    print(f"Power:\t\t\t{watt_to_hp(car['P']):.2f} hp,\t{car['P']:.2f} watts")
    # print(f"Drag coefficient:\t{car['Cd']}")
    # print(f"Frontal area:\t\t{car['A']} m²")
    # print(f"Rolling resistance:\t{car['Crr']}")


def print_simulation_info(data):
    print(f"Time:\t\t\t{data['quarter_time']:.2f} seconds")
    print(f"Speed:\t\t\t{ms_to_mph(data['quarter_speed']):.2f} mph,\t{data['quarter_speed']:.2f} m/s")
    print(f"0-60 mph:\t\t{data['0-60 mph']:.2f} seconds")

def hp_to_watt(hp):
    return hp * 745.7

def watt_to_hp(watt):
    return watt / 745.7

def mph_to_ms(mph):
    return mph * 0.44704

def ms_to_mph(ms):
    return ms / 0.44704

def kg_to_lb(kg):
    return kg * 2.20462

def lb_to_kg(lb):
    return lb / 2.20462

def in_to_m(inch):
    return inch * 0.0254

def sq_in_to_m2(sq_in):
    return sq_in * 0.00064516

def ms2_to_g(ms2):
    return ms2 / 9.81

def g_to_ms2(g):
    return g * 9.81

def lbft_to_nm(lbft):
    return lbft * 1.35582

def nm_to_lbft(nm):
    return nm / 1.35582

# Main function
def main():
    # Uncomment the car you want to simulate
    with open("cars.json", "r") as file:
        cars = json.load(file)

    for i in cars:
        if i["Name"] == "Honda Accord": # Change this to the car you want to simulate
            car = i
            break
            

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function to be executed in a separate thread
        future = executor.submit(simulate_quarter_mile, car)
            
        # Get the result from the future
        result = future.result()
        graph_and_print(car, result)

    # simulate_quarter_mile(car)
    # print(calc_top_speed(car))


    # Create a thread to run the simulation
    # simulation_thread = threading.Thread(target=simulate_quarter_mile, args=(car,))

    # Start the thread
    # simulation_thread.start()
    
    # Optionally, wait for the thread to finish
    # simulation_thread.join()

if __name__ == "__main__":
    main()


# DEPRICATED
# CAR DATA NOW IN cars.json
# ===========================================================================================================
# Preset cars
# Copy this to make your own car. Remember to convert units to metric.
# accord = {
#     "Name": "Honda Accord",     # name of the car
#     "Year": 2024,               # year of manufacture
#     "Drive Layout": "FF",       # FF, FR, 4WD, etc.
#     "Wheels": 4,                # number of wheels
#     "Driven Wheels": 2,         # number of driven wheels
#     "Engine": "2.0L I4 Turbo",  # engine displacement and type
#     "W": 1611,                  # weight in kg
#     "P": hp_to_watt(192),       # power in watts
#     "Cd": 0.27,                 # drag coefficient
#     "A": 2.24,                  # frontal area in m²
#     "Crr": 0.015,               # rolling resistance coefficient
#     "mu": 0.7,                  # coefficient of friction of tires
#     "redline": 6500,            # engine redline in rpm
#     "tire_diameter": 0.668,     # tire diameter in meters
#     "final_drive": 4.11*70,        # final drive ratio
#     "gear_ratios": [3.36, 
#                     2.13, 
#                     1.51, 
#                     1.13, 
#                     0.81, 
#                     0.67], # gear ratios
#     "torque_curve": [(0, 0),
#                      (1000, 165),
#                      (1600, 260),
#                      (5200, 260),
#                      (6000, 226),
#                      (6500, 180)] # torque curve in (rpm, nm)
# }

# is300 = {
#     "Name": "Lexus IS300",
#     "Year": 1998,
#     "Drive Layout": "FR",
#     "Wheels": 4,
#     "Driven Wheels": 2,
#     "Engine": "3.0L I6 NA",
#     "W": 1530,
#     "P": hp_to_watt(213),
#     "Cd": 0.29,
#     "A": 2.44,
#     "Crr": 0.015,
#     "mu": 0.7,
# }

# ioniq5n = {
#     "Name": "Hyundai Ioniq 5 N",     # name of the car
#     "Year": 2024,               # year of manufacture
#     "Drive Layout": "AWD",       # FF, FR, 4WD, etc.
#     "Wheels": 4,                # number of wheels
#     "Driven Wheels": 4,         # number of driven wheels
#     "Engine": "",  # engine displacement and type
#     "W": lb_to_kg(4861),                  # weight in kg
#     "P": 478000,       # power in watts
#     "Cd": 0.288,                 # drag coefficient
#     "A": 2.24,                  # frontal area in m²
#     "Crr": 0.015,               # rolling resistance coefficient
#     "mu": 1.42                   # coefficient of friction of tires
# }

# kart = {
#     "Name": "Yard Kart",     # name of the car
#     "Year": 2013,               # year of manufacture
#     "Drive Layout": "RR",       # FF, FR, 4WD, etc.
#     "Wheels": 4,                # number of wheels
#     "Driven Wheels": 2,         # number of driven wheels
#     "Engine": "212 Predator",  # engine displacement and type
#     "W": 136,                  # weight in kg
#     "P": hp_to_watt(6.5),       # power in watts
#     "Cd": 0.27,                 # drag coefficient
#     "A": 2.24,                  # frontal area in m²
#     "Crr": 0.015,               # rolling resistance coefficient
#     "mu": 0.7                   # coefficient of friction of tires
# }

# veyron = {
#     "Name": "Bugatti Veyron",     # name of the car
#     "Year": "2017 ish?",          # year of manufacture
#     "Drive Layout": "AWD",       # FF, FR, 4WD, etc.
#     "Wheels": 4,                # number of wheels
#     "Driven Wheels": 4,         # number of driven wheels
#     "Engine": "W16",  # engine displacement and type
#     "W": lb_to_kg(4486),                  # weight in kg
#     "P": hp_to_watt(1001),       # power in watts
#     "Cd": 0.36,                 # drag coefficient
#     "A": 2.07,                  # frontal area in m²
#     "Crr": 0.015,               # rolling resistance coefficient
#     "mu": 1                   # coefficient of friction of tires
# }

# fdrx7 = {
#     "Name": "Mazda RX-7 FD",    # name of the car
#     "Year": 2002,               # year of manufacture
#     "Drive Layout": "FR",       # FF, FR, 4WD, etc.
#     "Wheels": 4,                # number of wheels
#     "Driven Wheels": 2,         # number of driven wheels
#     "Engine": "1.3 13B Twin-Turbo Rotary",  # engine displacement and type
#     "W": 1300,                  # weight in kg
#     "P": hp_to_watt(255),       # power in watts
#     "Cd": 0.31,                 # drag coefficient
#     "A": 1.79,                  # frontal area in m²
#     "Crr": 0.015,               # rolling resistance coefficient
#     "mu": 1                   # coefficient of friction of tires
# }

# ===========================================================================================================