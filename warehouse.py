import math
import random

from robot import Robot
import selector as selector_mod
from selector import Action

NUM_CHARGERS = 5
NUM_ROBOTS = 5
WAREHOUSE_SIZE = 50
LOG = False

# The warehouse has the following shape:
# A line of chargers beginning at x=1, y=0 and going up to y=NUM_CHARGERS-1
# An empty "hallway" at x=0
# The items stored in the area bounded by x=-1,y=1,x=-WAREHOUSE_SIZE,y=WAREHOUSE_SIZE
# Human workers on the line y=-1 between x=-WAREHOUSE_SIZE,x=-1


class Warehouse:
    robots = None
    chargers = None
    time = 0
    items_picked = 0
    selector = selector_mod.selector

    def __init__(self, selector, write_to_file=False):
        if write_to_file:
            self.robots = [Robot(self, file=open("/home/charles/projects/cleanenergy-ai/data/robot{}.json".format(i), "w")) for i in range(NUM_ROBOTS)]
        else:
            self.robots = [Robot(self) for _ in range(NUM_ROBOTS)]
        self.chargers = [None for _ in range(NUM_CHARGERS)]
        self.selector = selector

    def chargers_available(self, robot):
        return sum((1 if (x is None or x == robot) else 0 for x in self.chargers))

    def tick(self):
        affected_robots = []
        for robot in self.robots:
            if robot.time > self.time:
                continue
            try:
                charger_i = self.chargers.index(robot)
                self.chargers[charger_i] = None
            except ValueError:
                pass
            action = self.selector(robot)
            if action == Action.CHARGE:
                try:
                    charger = self.chargers.index(None)
                except ValueError:
                    if LOG:
                        print("Unable to charge {}, chargers full".format(self.robots.index(robot)))
                    action = Action.IDLE
                if action != Action.IDLE:
                    if LOG:
                        print("Charging robot {} (at {}%) on charger {}".format(self.robots.index(robot), math.floor(robot.battery.charge * 100), charger))
                    s_move_time = robot.time
                    robot.move_to(0, charger)
                    robot.move_to(1, charger)
                    s_charge_time = robot.time
                    self.chargers[charger] = robot
                    robot.charge(min(1 - robot.battery.charge, 0.05))
                    e_charge_time = robot.time
            if action == Action.FETCH_ITEM:
                if robot.x != 0:
                    robot.move_to(0, robot.y)
                item_x = -random.randint(1, 10)
                item_y = (random.randint(1, 5) * 2) - 1
                picker = -random.randint(1, 10)
                if LOG:
                    # print("Sending robot {} to pick item on row {} for picker {}".format(self.robots.index(robot), item_y, -picker))
                    pass
                robot.move_to(0, item_y)
                robot.move_to(item_x, item_y)
                # Wait for pickup
                robot.pickup()
                robot.move_to(item_x, item_y + 1)
                robot.move_to(-11, item_y + 1)
                robot.move_to(-11, 0)
                robot.move_to(picker, 0)
                robot.move_to(picker, -1)
                # Wait for picker
                robot.time += (7 / 60)
                robot.move_to(picker, 0)
                robot.move_to(0, 0)
                robot.move_to(0, item_y + 1)
                robot.move_to(item_x, item_y + 1)
                robot.move_to(item_x, item_y)
                # Wait for setdown
                robot.setdown()
                robot.move_to(0, item_y)
                affected_robots.append(self.robots.index(robot))
                self.items_picked += 1

            else:
                robot.time += 1
        # for i in affected_robots:
        #     if LOG:
        #         print("Robot {} is at charge {}%".format(i, math.floor(self.robots[i].battery.charge * 100)))
        self.time = min(robot.time for robot in self.robots)
