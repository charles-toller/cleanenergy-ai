import math
from battery import Battery
from reward import reward
from selector import Action


class Robot:
    warehouse = None
    battery: Battery = None
    x = 0
    y = 0
    time = 0

    def __init__(self, warehouse, file=None):
        self.battery = Battery()
        self.warehouse = warehouse
        self.file = file

    def get_state(self):
        return [self.battery.charge, self.battery.lost_capacity, self.warehouse.chargers_available(self)]

    def calc_step(self, action: Action):
        state = self.get_state()
        next_state = None
        damage = 0
        if action == Action.CHARGE:
            charge_amount = min(1 - self.battery.charge, 0.05)
            time, damage = self.calc_charge(charge_amount)
            next_state = [state[0] + charge_amount, state[1] + damage, state[2] - 1]
        if action == Action.FETCH_ITEM:
            time, damage = self.calc_move_to(self.x, self.y - 50)
            next_state = [state[0] - (time / 100), state[1] + damage, state[2]]
        return next_state, reward(next_state, action, damage)

    def calc_move_to(self, x, y, need_damage=True):
        distance = abs(x - self.x) + abs(y - self.y)
        # Robots move at 2.5 units per second / 150 units per minute
        time = distance / 150
        damage = 0
        if need_damage:
            # Robots use 1% charge per minute to move
            damage = self.battery.calculate_damage((-time / 100, time))
        return time, damage

    def move_to(self, x, y):
        time, damage = self.calc_move_to(x, y, need_damage=False)
        # Robots use 1% charge per minute to move
        self.battery.run((-time / 100, time))
        if self.file is not None:
            self.file.write(
                "{{\"action\": \"move\", \"times\": [{},{}], \"pos\": [[{}, {}], [{}, {}]], \"charge\": {}}}\n".format(self.time, self.time + time, self.x, self.y, x, y, self.battery.charge))
        self.time += time
        self.x = x
        self.y = y

    def pickup(self):
        time = (3 / 60)
        if self.file is not None:
            self.file.write(
                "{{\"action\": \"pickup\", \"times\": [{},{}], \"charge\": {}}}\n".format(self.time, self.time + time, self.battery.charge))
        self.time += time

    def setdown(self):
        time = (3 / 60)
        if self.file is not None:
            self.file.write(
                "{{\"action\": \"setdown\", \"times\": [{},{}], \"charge\": {}}}\n".format(self.time, self.time + time, self.battery.charge))
        self.time += time

    def calc_charge(self, charge_amount, need_damage=True):
        time = charge_amount * 10
        damage = 0
        if need_damage:
            damage = self.battery.calculate_damage((charge_amount, time))
        return time, damage

    def charge(self, charge_amount):
        time, damage = self.calc_charge(charge_amount, need_damage=False)
        if self.file is not None:
            self.file.write(
                "{{\"action\": \"charge\", \"times\": [{},{}], \"charge\": {}}}\n".format(self.time, self.time + time, self.battery.charge + charge_amount))
        self.time += time
        self.battery.recharge_update_health(charge_amount)
