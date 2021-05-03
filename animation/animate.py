import math

from manim import *

from move_normally import Move
import json
import jsonlines

factor = 8 / 13
speed_factor = 10
class SquareToCircle(Scene):
    def translate_x_y(self, x, y):
        return x * factor, (y - 5) * factor

    def _create_shelf(self, i, j):
        s = Square(side_length=0.5)
        x, y = self.translate_x_y(-j - 1, (i * 2) + 1)
        s.move_to([x, y, 0])
        s.set_fill(BLUE, opacity=0.25)
        return s

    def _create_robot(self):
        s = Square(side_length=0.4)
        x, y = self.translate_x_y(0, 0)
        s.move_to([x, y, 0])
        s.set_stroke("#00FF00")
        s.set_fill("#00FF00", opacity=1)
        return s

    def move_list(self, obj, sx, sy, move_list):
        last = self.translate_x_y(sx, sy)
        last_time = 0
        for item in move_list:
            n = self.translate_x_y(item[0], item[1])
            yield Move(obj, last[0], last[1], n[0], n[1], run_time=item[2] - last_time)
            last = n
            last_time = item[2]

    def generate_color_updater(self, start_charge, end_charge):
        delta = end_charge - start_charge

        def updater(obj, alpha):
            target = start_charge + (delta * alpha)
            color = None
            if target > 0.5:
                color = interpolate_color("#FFFF00", "#00FF00", target - 0.5)
            else:
                color = interpolate_color("#FF0000", "#FFFF00", target)
            obj.set_stroke(color)
            obj.set_fill(color)

        return updater

    def generate_color_updater_reverse(self, start_charge, end_charge):
        delta = start_charge - end_charge

        def updater(obj, alpha):
            target = start_charge + (delta * alpha)
            color = None
            if target > 0.5:
                color = interpolate_color("#00FF00", "#FFFF00", target - 0.5)
            else:
                color = interpolate_color("#FFFF00", "#FF0000", target)
            obj.set_stroke(color)
            obj.set_fill(color)

        return updater

    def charge(self, obj, start_charge, end_charge, **kwargs):
        if start_charge == end_charge:
            return Animation(obj)
        if start_charge < end_charge:
            updater = self.generate_color_updater(start_charge, end_charge)
        else:
            updater = self.generate_color_updater_reverse(start_charge, end_charge)
        return UpdateFromAlphaFunc(obj, updater, **kwargs)

    def generate_follower(self, mobj):
        def follow(obj, alpha):
            if alpha == 0:
                return
            obj.move_to([mobj.get_x(), mobj.get_y(), 0])
        return follow

    def read_robot(self, filename, mobj):
        last_charge = 1
        last_time = 0
        x, y = 0, 0
        carrying = None
        with jsonlines.open("/home/charles/projects/cleanenergy-ai/data/{}".format(filename)) as reader:
            for obj in reader:
                if last_time != obj['times'][0]:
                    yield Wait(run_time=(obj['times'][0] - last_time) * speed_factor)
                run_time = (obj['times'][1] - obj['times'][0]) * speed_factor
                if obj['action'] == 'move':
                    sx, sy = self.translate_x_y(*obj['pos'][0])
                    ex, ey = self.translate_x_y(*obj['pos'][1])
                    x, y = obj['pos'][1]
                    yield AnimationGroup(
                        Move(mobj, sx, sy, ex, ey, run_time=run_time),
                        self.charge(mobj, last_charge, obj['charge'], run_time=run_time),
                        UpdateFromAlphaFunc(carrying, self.generate_follower(mobj)) if carrying is not None else Animation(mobj)
                    )
                elif obj['action'] == 'charge':
                    yield self.charge(mobj, last_charge, obj['charge'], run_time=run_time)
                elif obj['action'] == 'pickup':
                    i = int(math.floor((y - 1) / 2))
                    j = int(abs(x) - 1)
                    carrying = self.shelves[i][j]
                elif obj['action'] == 'setdown':
                    carrying = None
                last_charge = obj['charge']
                last_time = obj['times'][1]

    def construct(self):
        robots = [self._create_robot() for _ in range(0, 5)]
        robots_group = VGroup(*(robots[i] for i in range(0, 5)))
        self.shelves = [[self._create_shelf(i, j) for j in range(0, 10)] for i in range(0, 5)]
        shelves_group = VGroup(*(self.shelves[i][j] for j in range(9, -1, -1) for i in range(4, -1, -1)))
        chargers = Rectangle(height=5*factor, width=1*factor).move_to([*self.translate_x_y(1, 2), 0]).set_stroke(YELLOW)
        self.play(Create(shelves_group, lag_ratio=0.5))
        self.wait()
        self.play(Create(robots_group, lag_ratio=0))
        self.play(Create(chargers))
        shelvez = self.shelves[0][0].z_index
        for robot in robots:
            robot.z_index = shelvez - 1
        self.play(
            AnimationGroup(
                *(AnimationGroup(
                    *self.read_robot("robot{}.json".format(i), robots[i]),
                    lag_ratio=1
                ) for i in range(0, 5))
            )
        )
