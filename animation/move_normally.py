from manim import *


class Move(Transform):
    start = None
    stop = None
    label = None
    def __init__(self, mobject, sx, sy, ex, ey, start_time=None, end_time=None, **kwargs):
        self.start = mobject.copy().move_to([sx, sy, 0])
        self.stop = mobject.copy().move_to([ex, ey, 0])
        self.start_time = start_time
        self.end_time = end_time
        self.params = sx, sy, ex, ey
        super().__init__(mobject, **kwargs)
    def create_target(self) -> typing.Union[Mobject, None]:
        return self.stop

    def interpolate_submobject(
            self,
            submobject: Mobject,
            starting_submobject: Mobject,
            target_copy: Mobject,
            alpha: float,
    ) -> None:
        if alpha == 0:
            return
        submobject.interpolate(self.start, self.stop, alpha)
