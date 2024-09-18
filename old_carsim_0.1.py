# carsim 0.1

from time import sleep


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

    # Initial conditions
    v = 0   # initial velocity in m/s
    d = 0   # initial distance in meters
    t = 0   # initial time in seconds
    zerosixty_recorded = False

    print(Ft)

    # Simulation
    while d < quarter_mile:
        Fe = P_wheel / v if v > 0.01 else P / 0.01      # engine force in N
        Fd = 0.5 * Cd * A * rho * v**2                  # drag force in N
        Fr = Crr * W * g                                # rolling resistance force in N
        Fn = Fe - Fd - Fr                               # net force in N

        if Fn > Ft:
            Fn = Ft

        a = Fn / W                          # acceleration in m/s²

        v += a * delta_t                    # velocity in m/s
        d += v * delta_t                    # distance in meters
        t += delta_t                        # time in seconds

        if not zerosixty_recorded and v > mph_to_ms(60):
            zerosixty = t
            zerosixty_recorded = True

        # # Print realtime data
        # if t % 0.1 < delta_t:
        #     print(f"{t:.2f} s, {v:.2f} m/s, {d:.2f} m", end="\r")
        #     sleep(0.1)

        # # Print realtime data with newline
        if t % 0.1 < delta_t:
            print(f"{t:.2f} s, {v:.2f} m/s, {d:.2f} m")
            sleep(0.1)

    if not zerosixty_recorded:
        zerosixty = t    
    
    data = [t, v, zerosixty]

    print_car_info(car)
    print_simulation_info(data)

    return data

def calc_Ft(car):
    return (car["mu"] * car["W"] * 9.81) * (car["Driven Wheels"] / car["Wheels"])

def print_car_info(car):
    print(f"Car:\t\t\t{car['Year']} {car['Name']}")
    print(f"Weight:\t\t\t{kg_to_lb(car['W']):.2f} lb,\t{car['W']:.2f} kg")
    print(f"Power:\t\t\t{watt_to_hp(car['P']):.2f} hp,\t{car['P']:.2f} watts")
    print(f"Drag coefficient:\t{car['Cd']}")
    print(f"Frontal area:\t\t{car['A']} m²")
    print(f"Rolling resistance:\t{car['Crr']}")


def print_simulation_info(data):
    print(f"Time:\t\t\t{data[0]:.2f} seconds")
    print(f"Speed:\t\t\t{ms_to_mph(data[1]):.2f} mph,\t{data[1]:.2f} m/s")
    print(f"0-60 mph:\t\t{data[2]:.2f} seconds")

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


# ===========================================================================================================
# Preset cars
# Copy this to make your own car. Remember to convert units to metric.
accord = {
    "Name": "Honda Accord",     # name of the car
    "Year": 2024,               # year of manufacture
    "Drive Layout": "FF",       # FF, FR, 4WD, etc.
    "Wheels": 4,                # number of wheels
    "Driven Wheels": 2,         # number of driven wheels
    "Engine": "2.0L I4 Turbo",  # engine displacement and type
    "W": 1611,                  # weight in kg
    "P": hp_to_watt(192),       # power in watts
    "Cd": 0.27,                 # drag coefficient
    "A": 2.24,                  # frontal area in m²
    "Crr": 0.015,               # rolling resistance coefficient
    "mu": 0.7                   # coefficient of friction of tires
}

is300 = {
    "Name": "Lexus IS300",
    "Year": 1998,
    "Drive Layout": "FR",
    "Wheels": 4,
    "Driven Wheels": 2,
    "Engine": "3.0L I6 NA",
    "W": 1530,
    "P": hp_to_watt(213),
    "Cd": 0.29,
    "A": 2.44,
    "Crr": 0.015,
    "mu": 0.7,
}

ioniq5n = {
    "Name": "Hyundai Ioniq 5 N",     # name of the car
    "Year": 2024,               # year of manufacture
    "Drive Layout": "AWD",       # FF, FR, 4WD, etc.
    "Wheels": 4,                # number of wheels
    "Driven Wheels": 4,         # number of driven wheels
    "Engine": "",  # engine displacement and type
    "W": lb_to_kg(4861),                  # weight in kg
    "P": 478000,       # power in watts
    "Cd": 0.288,                 # drag coefficient
    "A": 2.24,                  # frontal area in m²
    "Crr": 0.015,               # rolling resistance coefficient
    "mu": 1.42                   # coefficient of friction of tires
}

kart = {
    "Name": "Yard Kart",     # name of the car
    "Year": 2013,               # year of manufacture
    "Drive Layout": "RR",       # FF, FR, 4WD, etc.
    "Wheels": 4,                # number of wheels
    "Driven Wheels": 2,         # number of driven wheels
    "Engine": "212 Predator",  # engine displacement and type
    "W": 136,                  # weight in kg
    "P": hp_to_watt(6.5),       # power in watts
    "Cd": 0.27,                 # drag coefficient
    "A": 2.24,                  # frontal area in m²
    "Crr": 0.015,               # rolling resistance coefficient
    "mu": 0.7                   # coefficient of friction of tires
}

veyron = {
    "Name": "Bugatti Veyron",     # name of the car
    "Year": "2017 ish?",          # year of manufacture
    "Drive Layout": "AWD",       # FF, FR, 4WD, etc.
    "Wheels": 4,                # number of wheels
    "Driven Wheels": 4,         # number of driven wheels
    "Engine": "W16",  # engine displacement and type
    "W": lb_to_kg(4486),                  # weight in kg
    "P": hp_to_watt(1001),       # power in watts
    "Cd": 0.36,                 # drag coefficient
    "A": 2.07,                  # frontal area in m²
    "Crr": 0.015,               # rolling resistance coefficient
    "mu": 1                   # coefficient of friction of tires
}

fdrx7 = {
    "Name": "Mazda RX-7 FD",    # name of the car
    "Year": 2002,               # year of manufacture
    "Drive Layout": "FR",       # FF, FR, 4WD, etc.
    "Wheels": 4,                # number of wheels
    "Driven Wheels": 2,         # number of driven wheels
    "Engine": "1.3 13B Twin-Turbo Rotary",  # engine displacement and type
    "W": 1300,                  # weight in kg
    "P": hp_to_watt(255),       # power in watts
    "Cd": 0.31,                 # drag coefficient
    "A": 1.79,                  # frontal area in m²
    "Crr": 0.015,               # rolling resistance coefficient
    "mu": 0.7                   # coefficient of friction of tires
}

# ===========================================================================================================

# Main function
def main():
    # Uncomment the car you want to simulate

    # car = accord
    # car = is300
    # car = ioniq5n
    # car = kart
    # car = veyron
    car = fdrx7

    simulate_quarter_mile(car)

if __name__ == "__main__":
    main()
