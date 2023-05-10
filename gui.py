import tkinter as tk
from tkinter import ttk
from track import Track
from car import Car
import math


class App(tk.Tk):
    def __init__(self, restart_func):
        super().__init__()

        self.window_width = 1500
        self.window_height = 1000

        self.title("Maze")

        self.style = ttk.Style(self)
        self.style.configure("Bigger.TLabel", font=("Helvetica", 20))

        # get the screen dimension
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(self.screen_width / 2 - self.window_width / 2)
        center_y = int(self.screen_height / 2 - self.window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)

        self.canvas_frame = CanvasFrame(self)
        self.canvas_frame.grid(column=0, row=0, sticky='NSEW')

        self.button_frame = ButtonFrame(self, restart_func)
        self.button_frame.grid(column=1, row=0, sticky='NSEW')

    def draw_track(self, track):
        self.canvas_frame.draw_track(track)

    def draw_car(self, car):
        self.canvas_frame.draw_car(car)

    def draw_timer(self):
        self.canvas_frame.draw_timer()


class CanvasFrame(tk.Frame):
    canvas_width = 804
    canvas_height = 804

    '''
    track in format:
    int track_width
    int track_height
    bool[][] track_tiles (0 if there is no track, 1 if there is)
    ((int, int), (int, int))[] track_boundaries (track wall)
    ((int, int), (int, int))[] track_checkpoints
    ((int, int), (int, int)) track_start
    '''
    def draw_track(self, track):
        self.p = 4
        self.tile_width = (self.canvas_width-self.p) / track.width
        self.tile_height = (self.canvas_height-self.p) / track.height
        # print(track.tiles)
        for i in range(track.height):
            for j in range(track.width):
                if track.tiles[i][j]:
                    self.canvas.create_rectangle((self.p+j*self.tile_width, self.p+i*self.tile_height),
                                                 (self.p+(j+1)*self.tile_width, self.p+(i+1)*self.tile_height),
                                                 fill='#787878', width=0)

        for boundary in track.boundaries:
            self.canvas.create_line(self.p+boundary[0][0] * self.tile_width, self.p+boundary[0][1] * self.tile_height,
                                    self.p+boundary[1][0] * self.tile_width, self.p+boundary[1][1] * self.tile_height,
                                    width=4)

        for checkpoint in track.checkpoints:
            self.canvas.create_line(self.p+checkpoint[0][0] * self.tile_width, self.p+checkpoint[0][1] * self.tile_height,
                                    self.p+checkpoint[1][0] * self.tile_width, self.p+checkpoint[1][1] * self.tile_height,
                                    width=4, fill="#185bbf")

        self.canvas.create_line(self.p+track.start[0][0] * self.tile_width, self.p+track.start[0][1] * self.tile_height,
                                self.p+track.start[1][0] * self.tile_width, self.p+track.start[1][1] * self.tile_height,
                                width=4, fill="#fc3b1e")

    def draw_car(self, car):
        for rm in self.to_remove:
            self.canvas.delete(rm)
        self.to_remove = []

        car_points = car.get_points()
        points = [(self.p + car_points[i][0] * self.tile_width,
                   self.p + car_points[i][1] * self.tile_height)
                   for i in range(len(car_points))]

        car_id = self.canvas.create_polygon(points)
        self.to_remove.append(car_id)

        front_axle_middle = [(points[0][0] + points[3][0]) / 2, (points[0][1] + points[3][1]) / 2]
        tire_direction = [50 * math.cos(car.angle + car.tire_angle) + front_axle_middle[0],
                          -50 * math.sin(car.angle + car.tire_angle) + front_axle_middle[1]]
        velocity_direction = [50 * math.cos(car.velocity_direction) + front_axle_middle[0],
                              -50 * math.sin(car.velocity_direction) + front_axle_middle[1]]

        line_id = self.canvas.create_line(front_axle_middle[0], front_axle_middle[1], tire_direction[0], tire_direction[1],
                                               width=4, fill="#3cc10f")
        self.to_remove.append(line_id)

        line_id = self.canvas.create_line(front_axle_middle[0], front_axle_middle[1], velocity_direction[0], velocity_direction[1],
                                               width=2, fill="#4288f7")
        self.to_remove.append(line_id)

    def draw_timer(self):
        if self.timer_id is not None:
            self.canvas.delete(self.timer_id)
            self.timer_id = None

        if self.timer != -1:
            self.timer_id = self.canvas.create_text((self.canvas_width / 2, self.canvas_height / 2),
                                                    text=str(self.timer), font=("Helvetica", 40))

    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.timer_id = None
        self.to_remove = []
        self.line_id = None
        self.car_id = None
        self.tile_height = None
        self.tile_width = None
        self.p = None
        self.maze_width = None
        self.maze_height = None
        self.timer = -1

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#9af48d')
        self.canvas.pack(anchor=tk.CENTER, expand=True)


class ButtonFrame(tk.Frame):
    def __init__(self, master, restart_func, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)

        restart_button = ttk.Button(self, text="Restart", command=restart_func)
        restart_button.grid(column=0, row=0, sticky='NSWE')

        self.vel = tk.StringVar(value=0)
        vel_meter = ttk.Label(self, textvariable=self.vel, style="Bigger.TLabel")
        vel_meter.grid(column=0, row=1)

        self.time = tk.StringVar(value=0)
        time_meter = ttk.Label(self, textvariable=self.time, style="Bigger.TLabel")
        time_meter.grid(column=0, row=2)

        self.checkpoints = tk.StringVar(value=0)
        checkpoints_meter = ttk.Label(self, textvariable=self.checkpoints, style="Bigger.TLabel")
        checkpoints_meter.grid(column=0, row=3)

        self.top_time = None
        self.top_time_var = tk.StringVar(value="Top Time: None")
        top_time_meter = ttk.Label(self, textvariable=self.top_time_var, style="Bigger.TLabel")
        top_time_meter.grid(column=0, row=4)
