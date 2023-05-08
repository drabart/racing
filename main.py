from gui import *
from track import Track
from car import Car
import math
# from agent import *


class Master:
    root = None
    track_width = 7
    track_height = 7
    track_tiles = [[0, 0, 0, 0, 0, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1],
                   [1, 0, 1, 1, 1, 1, 1],
                   [1, 0, 0, 0, 0, 0, 1],
                   [1, 1, 1, 0, 0, 0, 1],
                   [0, 1, 1, 0, 0, 0, 1],
                   [0, 1, 1, 1, 1, 1, 1]]
    track_boundaries = [((0, 1), (0, 5)),
                        ((1, 2), (1, 4)),
                        ((1, 5), (1, 7)),
                        ((2, 2), (2, 3)),
                        ((3, 1), (3, 2)),
                        ((3, 4), (3, 6)),
                        ((5, 0), (5, 2)),
                        ((6, 1), (6, 6)),
                        ((7, 0), (7, 7)),
                        ((5, 0), (7, 0)),
                        ((0, 1), (3, 1)),
                        ((1, 2), (2, 2)),
                        ((3, 2), (5, 2)),
                        ((2, 3), (6, 3)),
                        ((1, 4), (3, 4)),
                        ((0, 5), (2, 5)),
                        ((2, 6), (6, 6)),
                        ((1, 7), (7, 7))]
    track_checkpoints = [((6, 3), (7, 3)),
                         ((6, 0), (6, 1)),
                         ((5, 2), (6, 2)),
                         ((4, 2), (4, 3)),
                         ((2, 2), (3, 2)),
                         ((1, 1), (1, 2)),
                         ((0, 3), (1, 3)),
                         ((1, 4), (1, 5)),
                         ((2, 5), (3, 5)),
                         ((1, 6), (2, 6)),
                         ((3, 6), (3, 7)),
                         ((5, 6), (5, 7)),
                         ((6, 6), (7, 6))]
    track_start = ((6, 4), (7, 4))
    track = Track(track_width, track_height, track_tiles, track_boundaries, track_checkpoints, track_start)
    car = None

    def restart_race(self):
        print("Restarting race")
        self.car = Car([6.5, 13.0 / 3.0], math.pi / 2.0)
        self.root.draw_track(self.track)
        self.root.draw_car(self.car)
        print("Race Restarted")

    def _set_bindings(self):
        for char in ["w", "s", "a", "d", "r"]:
            self.root.bind("<KeyPress-%s>" % char, self._pressed)
            self.root.bind("<KeyRelease-%s>" % char, self._released)
            self.pressed[char] = False

    def _pressed(self, event):
        self.pressed[event.char] = True

    def _released(self, event):
        self.pressed[event.char] = False

    def _animate(self):
        # update car
        is_accelerating = False
        tire_change = 0
        breaking = 0
        reverse = 0
        if self.pressed["w"]:
            is_accelerating = True
        if self.pressed["a"]:
            tire_change += 1
        if self.pressed["d"]:
            tire_change -= 1
        if self.pressed["s"]:
            breaking = 1
        if self.pressed["r"]:
            reverse = 1
        self.car.update(10 / 1000, tire_change, is_accelerating, breaking, reverse)
        self.root.draw_car(self.car)
        self.car.check_collisions(self.track_boundaries)

        # update gui
        self.root.button_frame.vel.set(round(self.car.get_vel(), 3))

        self.root.after(10, self._animate)

    def __init__(self):
        # pass arguments and function names for buttons to work
        self.pressed = {}
        self.root = App(self.restart_race)
        # run root
        self._set_bindings()

        self.restart_race()

        self._animate()
        self.root.mainloop()


def main():
    master = Master()


if __name__ == "__main__":
    main()
