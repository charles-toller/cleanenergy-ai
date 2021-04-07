import math

from warehouse import Warehouse

warehouse = Warehouse()
i = 0
while warehouse.time < 525600:
    warehouse.tick()
    if i % 1e5 == 0:
        print("Day {}".format(math.ceil(warehouse.time / 1440)))
    i += 1
print("Ran for {} days".format(math.ceil(warehouse.time / 1440)))
print("Picked {} items with {} robots and {} chargers".format(warehouse.items_picked, len(warehouse.robots), len(warehouse.chargers)))
for robot in warehouse.robots:
    print("Battery Health: {}".format(math.floor((1-robot.battery.lost_capacity) * 100)))
