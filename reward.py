from selector import Action


def reward(state, action, damage):
    charge, health, chargers = state
    reward = 0
    if action == Action.FETCH_ITEM:
        reward = 1
    if damage > 0:
        # Battery replacements at 80%, costing $10,000 per robot
        reward += (damage * -50000)
    if action == Action.CHARGE and charge == 1.0:
        reward = -100
    return reward
