from manim import *
class SquareTest(Scene):
    def construct(self):
        s1 = Square(side_length=0.5).move_to([-1, 0, 0])
        s2 = Square(side_length=0.5)
        self.play(Create(s1))
        self.play(Create(s2))
        self.play(AnimationGroup(
            AnimationGroup(
                s1.animate(run_time=3).move_to([-2, 0, 0]),
                s1.animate(run_time=2).move_to([-2, 1, 0]),
                lag_ratio=1
            ),
            AnimationGroup(
                s2.animate(run_time=2).move_to([1, 0, 0]),
                s2.animate(run_time=3).move_to([1, 2, 0]),
                lag_ratio=1
            )
        ))
