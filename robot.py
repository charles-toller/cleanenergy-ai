import math
from battery import Battery


class Robot:
    battery: Battery = None
    x = 0
    y = 0
    time = 0

    def __init__(self):
        self.battery = Battery()

    def move_to(self, x, y):
        distance = abs(x - self.x) + abs(y - self.y)
        self.x = x
        self.y = y
        # Robots move at 2.5 units per second / 150 units per minute
        time = distance / 150
        # Robots use 1% charge per minute to move
        self.battery.run((-time / 100, time))
        self.time += time

    def charge(self, charge_amount):
        self.time += charge_amount * 10
        self.battery.recharge_update_health(charge_amount)
