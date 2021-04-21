from battery import Battery

bat_deep = Battery()
bat_norm = Battery()
bat_shallow = Battery()
bat_shallow_mid = Battery()
bat_shallow_mid.charge = 0.5
bat_shallow_mid.start_charge = 0.5
for i in range(0, 900):
    bat_deep.run((-1, 270))
    bat_deep.recharge_update_health(1)
    bat_norm.run((-0.5, 135))
    bat_norm.recharge_update_health(0.5)
    bat_norm.run((-0.5, 135))
    bat_norm.recharge_update_health(0.5)
    for j in range(0, 5):
        bat_shallow.run((-0.1, 30))
        bat_shallow.recharge_update_health(0.1)
    for j in range(0, 5):
        bat_shallow_mid.run((-0.1, 30))
        bat_shallow_mid.recharge_update_health(0.1)
print("900 Full Discharges: " + str(bat_deep.lost_capacity))
print("1800 Half Discharges: " + str(bat_norm.lost_capacity))
print("4500 100-90 Discharges: " + str(bat_shallow.lost_capacity))
print("4500 50-40 Discharges: " + str(bat_shallow_mid.lost_capacity))
