from gui import *
from track import Track
from car import Car
import math
import time
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
    lap_time = 0
    last_10_frames = []
    start_time = 0

    def _restart_race(self, event=None):
        print("Restarting race")
        self.lap_time = 0
        self.free_car = False
        self.car = Car([6.5, 13.0 / 3.0], math.pi / 2.0)
        self.root.draw_track(self.track)
        self.root.draw_car(self.car)

        self._timer(0)
        print("Race Restarted")

    def _timer(self, seconds):
        if seconds == 3:
            self.free_car = True
            self.lap_time = 1
            self.root.canvas_frame.timer = -1
        else:
            self.root.canvas_frame.timer = 3 - seconds
            self.root.after(1000, self._timer, seconds + 1)

    def _set_bindings(self):
        for char in ["w", "s", "a", "d", "r"]:
            self.root.bind("<KeyPress-%s>" % char, self._pressed)
            self.root.bind("<KeyRelease-%s>" % char, self._released)
            self.pressed[char] = False

        self.root.bind("q", self._restart_race)

    def _pressed(self, event):
        self.pressed[event.char] = True

    def _released(self, event):
        self.pressed[event.char] = False

    def _animate(self):
        # print((time.time_ns() - self.start_time) / (10 ** 9))

        while len(self.last_10_frames) >= 10:
            self.last_10_frames.remove(self.last_10_frames[0])
        last_frame = (time.time_ns() - self.start_time) / (10 ** 9)
        self.last_10_frames.append(last_frame)

        self.start_time = time.time_ns()

        # handle inputs
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

        # update car if not frozen
        if self.free_car:
            self.car.update(10 / 1000, tire_change, is_accelerating, breaking, reverse)
            self.car.check_collisions(self.track.boundaries)

        # checkpoint handling
        self.car.check_checkpoints(self.track.checkpoints)
        if self.car.check_finish(self.track.start):
            finish_time = self.lap_time / 100
            if self.root.button_frame.top_time is None or self.root.button_frame.top_time > finish_time:
                self.root.button_frame.top_time = finish_time
                self.root.button_frame.top_time_var.set("Top Time: " + str(finish_time))
            self.lap_time = 1

        # gui render
        self.root.draw_car(self.car)
        self.root.draw_timer()
        self.root.draw_rays([0, math.pi / 3, math.pi / 6, -math.pi / 3, -math.pi / 6], self.track.boundaries, self.car)

        # update gui
        vel_str = str(round(self.car.get_vel(), 3))
        self.root.button_frame.vel.set("Velocity: " + vel_str + "0" * (5 - len(vel_str)))

        time_str = "0.0"
        if self.lap_time != 0:
            time_str = str(self.lap_time / 100)
        self.mx_time_str = max(self.mx_time_str, len(time_str))
        self.root.button_frame.time.set("Time: " + time_str + "0" * (self.mx_time_str - len(time_str)))

        self.root.button_frame.checkpoints.set("Checkpoints: " + str(self.car.next_checkpoint))

        if self.free_car:
            self.lap_time += 1

        self.root.button_frame.fps.set("FPS: " + str(1 / (sum(self.last_10_frames) / len(self.last_10_frames))))

        # schedule next frame
        self.root.after(10, self._animate)

    def __init__(self):
        # pass arguments and function names for buttons to work
        self.mx_time_str = 5
        self.free_car = False
        self.pressed = {}
        self.root = App(self._restart_race)
        # run root
        self._set_bindings()

        self._restart_race()

        self._animate()
        self.root.mainloop()


def main():
    master = Master()


if __name__ == "__main__":
    main()
