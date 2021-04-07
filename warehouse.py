import math
import random

from robot import Robot

NUM_CHARGERS = 1
NUM_ROBOTS = 5
WAREHOUSE_SIZE = 50
LOG = False

# The warehouse has the following shape:
# A line of chargers beginning at x=1, y=0 and going up to y=NUM_CHARGERS-1
# An empty "hallway" at x=0
# The items stored in the area bounded by x=-1,y=1,x=-WAREHOUSE_SIZE,y=WAREHOUSE_SIZE
# Human workers on the line y=-1 between x=-WAREHOUSE_SIZE,x=-1

from selector import *


class Warehouse:
    robots = None
    chargers = None
    time = 0
    items_picked = 0

    def __init__(self):
        self.robots = [Robot() for _ in range(NUM_ROBOTS)]
        self.chargers = [None for _ in range(NUM_CHARGERS)]

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
            action = selector(robot)
            if action == Action.CHARGE:
                robot.move_to(0, 0)
                try:
                    charger = self.chargers.index(None)
                except ValueError:
                    if LOG:
                        print("Unable to charge {}, chargers full".format(self.robots.index(robot)))
                    action = Action.IDLE
                if action != Action.IDLE:
                    if LOG:
                        print("Charging robot {} (at {}%) on charger {}".format(self.robots.index(robot), math.floor(robot.battery.charge * 100), charger))
                    robot.move_to(0, charger)
                    robot.move_to(1, charger)
                    self.chargers[charger] = robot
                    robot.charge(1 - robot.battery.charge)
            if action == Action.FETCH_ITEM:
                item_y = random.randint(1, 100)
                picker = -random.randint(1, 100)
                if LOG:
                    print("Sending robot {} to pick item on row {} for picker {}".format(self.robots.index(robot), item_y, -picker))
                robot.move_to(0, item_y)
                robot.move_to(-101, item_y)
                robot.move_to(-101, -1)
                robot.move_to(picker, -1)
                affected_robots.append(self.robots.index(robot))
                self.items_picked += 1
            else:
                robot.time += 1
        for i in affected_robots:
            if LOG:
                print("Robot {} is at charge {}%".format(i, math.floor(self.robots[i].battery.charge * 100)))
        self.time = min(robot.time for robot in self.robots)
