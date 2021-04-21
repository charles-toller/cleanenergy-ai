from selector import Action


def reward(state, action, damage):
    charge, health, chargers = state
    if chargers < 0:
        return -1e8
    if charge < 0:
        return charge * 1e8
    reward = 0
    if action == Action.FETCH_ITEM:
        reward = 1
    if damage > 0:
        # Battery replacements at 80%, costing $10,000 per robot
        reward += (damage * -50000)
    return reward
