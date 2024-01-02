from gui import *
from track import Track
from car import Car
import math
import time
import neat
import pickle
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
    last_10_frames = []
    start_time = 0

    def _restart_race(self, event=None):
        print("Restarting race")
        self.free_car = False
        self.car = Car([6.5, 13.0 / 3.0], math.pi / 2.0)
        self.car.lap_time = 0
        self.root.draw_track(self.track)
        self.root.draw_car(self.car)

        self._timer(0)
        print("Race Restarted")

    def _timer(self, seconds):
        if seconds == 3:
            self.free_car = True
            self.car.lap_time = 1
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

    def _start_training(self):
        self.train = True
        self.root.clear()
        self.root.canvas_frame.timer = -1
        self.root.canvas_frame.draw_timer()

        self.max_fitness = 0

        config_path = "./config-feedforward.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

        population = neat.population.Population(config)

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        population.run(self._run_training, 1000)

        self.train = False
        self._animate()
        self._restart_race()

    def _run_training(self, genomes, config):
        self.genomes = genomes
        self.nets = []
        self.cars = []

        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0

            # Init my cars
            self.cars.append(Car([6.5, 13.0 / 3.0], math.pi / 2.0))

        self.generation += 1
        self.generation_finished = False

        while not self.generation_finished:
            self._training_frame()

        best_genome = None
        better = False
        for genome in self.genomes:
            if genome[1].fitness > self.max_fitness:
                best_genome = genome[1]
                self.max_fitness = genome[1].fitness
                better = True

        if better:
            path = "models/generation" + str(best_genome.fitness) + ".pyc"
            pickle.dump(best_genome, open(path, "wb"))

    def _update_fps(self):
        while len(self.last_10_frames) >= 10:
            self.last_10_frames.remove(self.last_10_frames[0])
        last_frame = (time.time_ns() - self.start_time) / (10 ** 9)
        self.last_10_frames.append(last_frame)

        self.start_time = time.time_ns()

    def _training_frame(self):
        # Input my data and get result from network
        # print(self.generation)
        self._update_fps()

        tire_change = []
        is_accelerating = []
        breaking = []
        reverse = []
        for index, car in enumerate(self.cars):
            output = self.nets[index].activate(car.get_data(self.track.boundaries, self.track.checkpoints, self.track.start))
            tc = 0
            if output[0] > 0:
                tc += 1
            if output[1] > 0:
                tc -= 1
            tire_change.append(tc)
            acc = 0
            if output[2] > 0:
                acc = 1
            is_accelerating.append(acc)
            br = 0
            if output[3] > 0:
                br = 1
            breaking.append(br)
            rv = 0
            # if output[4] > 0:
            #    rv = 1
            reverse.append(rv)

        # Update car and fitness
        remain_cars = 0
        max_lap_time = 0
        for i, car in enumerate(self.cars):
            if car.lifespan > 0:
                remain_cars += 1
                car.update(10 / 1000, tire_change[i], is_accelerating[i], breaking[i], reverse[i])
                car.check_collisions(self.track.boundaries)
                car.check_checkpoints(self.track.checkpoints)
                if car.next_checkpoint > self.root.button_frame.cp:
                    self.root.button_frame.cp = car.next_checkpoint
                    self.root.button_frame.checkpoints.set("Checkpoints: " + str(car.next_checkpoint))

                if car.check_finish(self.track.start):
                    finish_time = car.lap_time / 100
                    if self.root.button_frame.top_time is None or self.root.button_frame.top_time > finish_time:
                        self.root.button_frame.top_time = finish_time
                        self.root.button_frame.top_time_var.set("Top Time: " + str(finish_time))
                    car.lap_time = 1

                max_lap_time = max(max_lap_time, car.lap_time)
                self.genomes[i][1].fitness = car.fitness
            else:
                car.dead = True

        self.root.clear()

        # check
        if remain_cars == 0:
            self.generation_finished = True

        if self.generation % 5 != 0:
            return

        # interface takes approximately 1s per car per generation
        # Drawing
        for car in self.cars:
            if not car.dead:
                self.root.draw_car(car)

        # Gui
        fps_str = str(round(1 / (sum(self.last_10_frames) / len(self.last_10_frames)), 3))
        self.root.button_frame.fps.set("FPS: " + fps_str + (6 - len(fps_str)) * "0")

        time_str = str(max_lap_time / 100)
        self.mx_time_str = max(self.mx_time_str, len(time_str))
        self.root.button_frame.time.set("Time: " + time_str + "0" * (self.mx_time_str - len(time_str)))

        self.root.update()

    def _pressed(self, event):
        self.pressed[event.char] = True

    def _released(self, event):
        self.pressed[event.char] = False

    def _animate(self):
        # print((time.time_ns() - self.start_time) / (10 ** 9))

        self._update_fps()

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
            finish_time = self.car.lap_time / 100
            if self.root.button_frame.top_time is None or self.root.button_frame.top_time > finish_time:
                self.root.button_frame.top_time = finish_time
                self.root.button_frame.top_time_var.set("Top Time: " + str(finish_time))
            self.car.lap_time = 1

        # gui render
        self.root.clear()
        self.root.draw_car(self.car)
        self.root.draw_timer()
        self.root.draw_rays([0, math.pi / 3, math.pi / 6, -math.pi / 3, -math.pi / 6], self.track.boundaries, self.car)

        # update gui
        vel_str = str(round(self.car.get_vel(), 3))
        self.root.button_frame.vel.set("Velocity: " + vel_str + "0" * (5 - len(vel_str)))

        time_str = "0.0"
        if self.car.lap_time != 0:
            time_str = str(self.car.lap_time / 100)
        self.mx_time_str = max(self.mx_time_str, len(time_str))
        self.root.button_frame.time.set("Time: " + time_str + "0" * (self.mx_time_str - len(time_str)))

        self.root.button_frame.checkpoints.set("Checkpoints: " + str(self.car.next_checkpoint))

        fps_str = str(round(1 / (sum(self.last_10_frames) / len(self.last_10_frames)), 3))
        self.root.button_frame.fps.set("FPS: " + fps_str + (6 - len(fps_str)) * "0")

        # schedule next frame
        if not self.train:
            self.root.after(10, self._animate)

    def __init__(self):
        # pass arguments and function names for buttons to work
        self.generation = 0
        self.generation_finished = False
        self.train = False
        self.mx_time_str = 5
        self.free_car = False
        self.pressed = {}
        self.root = App(self._restart_race, self._start_training)
        # run root
        self._set_bindings()

        self._restart_race()

        self._animate()
        self.root.mainloop()


def main():
    master = Master()


if __name__ == "__main__":
    main()
