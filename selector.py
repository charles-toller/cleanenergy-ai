from enum import Enum


class Action(Enum):
    CHARGE = 1
    FETCH_ITEM = 2
    IDLE = 3


def selector(robot):
    if robot.battery.charge < 0.05:
        return Action.CHARGE
    return Action.FETCH_ITEM
