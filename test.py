from battery import Battery

bat_deep = Battery()
bat_shallow = Battery()
bat_shallow_mid = Battery()
for i in range(0, 200):
    bat_deep.run((-1, 270))
    bat_deep.recharge_update_health(1)
    bat_shallow.run((-0.5, 135))
    bat_shallow.recharge_update_health(0.5)
    bat_shallow.run((-0.5, 135))
    bat_shallow.recharge_update_health(0.5)
    for j in range(0, 5):
        bat_shallow_mid.run((-0.1, 30))
        bat_shallow_mid.recharge_update_health(0.1)
print(bat_deep.lost_capacity)
print(bat_shallow.lost_capacity)
print(bat_shallow_mid.lost_capacity)
