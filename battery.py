import math
from functools import reduce

# These constants are modeled after a "typical" vehicle rechargable battery
kco = 0.0000366
kex = 0.717
ksoc = 0.916
t = 35
ta = t + 273
tnom = 25
tnabs = tnom + 273
factor_1 = kex * tnabs / ta
tfact = 0.0693
L = 0.2


class Battery:
    # [0,1] representing current charge capacity, with 1 being completely full.
    charge = 1
    # A capacity of less than 0.8 is considered "dead"
    # This is the LOST capacity, so this number goes up over time as the battery degrades
    lost_capacity = 0
    # This is a list of tuples, each in the form of (amount,tsecs) for the amount charged over a certain timeframe
    # For discharges, this should be negative. For example, driving to a shelf might look like: (-0.01, 15)
    # This also needs to contain idle intervals. Just insert (0, length)
    start_charge = 1
    charge_intervals = None

    def __init__(self):
        self.charge_intervals = []

    def calculate_damage(self, next_movement):
        # This code is based of the following paper: https://ieeexplore-ieee-org.dist.lib.usu.edu/stamp/stamp.jsp?tp=&arnumber=5619782
        # Also written in a caffeine-induced rage, don't touch
        with_start_intervals = []
        last = self.start_charge
        for i in range(0, len(self.charge_intervals)):
            delta, time = self.charge_intervals[i]
            with_start_intervals.append((last + delta, time * 60))
            last += delta
        with_start_intervals.append((next_movement[0] + last, next_movement[1] * 60))
        duration = sum(y for x, y in with_start_intervals)
        soc_avg = (self.start_charge + with_start_intervals[0][0]) * with_start_intervals[0][1] / 2
        for i in range(1, len(with_start_intervals)):
            last_charge, _ = with_start_intervals[i - 1]
            curr_charge, length = with_start_intervals[i]
            a = last_charge + curr_charge
            a *= length / 2
            soc_avg += a
        soc_avg /= duration
        k = 0
        last = self.start_charge
        for i in range(0, len(with_start_intervals)):
            target, time = with_start_intervals[i]
            delta = last-target
            last = target
            if time == 0 or delta == 0:
                continue
            k += ((time*pow(last+(delta*time/time)-soc_avg, 3))/3*delta) - ((time*pow(last-soc_avg, 3))/3*delta)
        soc_dev = 2*math.sqrt(3*k/duration)
        low = min(x for x, _ in with_start_intervals)
        charged_to = with_start_intervals[len(with_start_intervals) - 1][0]
        cycle = self.start_charge - low
        if low != charged_to:
            cycle += (charged_to - low)
            cycle /= 2
        life = cycle * kco * (1 - L) * math.exp(((soc_dev - 1) / kex * tnabs / ta) + (ksoc * (soc_avg - 0.5) * 4) + (tfact * (t - tnom) * (tnabs / ta)))
        return life

    def run(self, movement):
        self.charge_intervals.append(movement)
        self.charge += movement[0]

    def recharge_update_health(self, charge_amount):
        # Charging from empty -> full takes approximately 10 minutes
        damage = self.calculate_damage((charge_amount, charge_amount * 10))
        self.lost_capacity += damage
        self.charge += charge_amount
        self.start_charge = self.charge
        self.charge_intervals = []
