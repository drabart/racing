import math
from copy import deepcopy


class Car:
    @staticmethod
    def decompose_vector(vector, line):
        x1, y1 = line[0]
        x2, y2 = line[1]

        # calculate the unit vector of the line
        line_vector = (x2 - x1, y2 - y1)
        line_magnitude = math.sqrt(line_vector[0] ** 2 + line_vector[1] ** 2)
        line_unit_vector = (line_vector[0] / line_magnitude, line_vector[1] / line_magnitude)

        # calculate the projection of the vector onto the line
        projection_magnitude = vector[0] * line_unit_vector[0] + vector[1] * line_unit_vector[1]
        projection_vector = (projection_magnitude * line_unit_vector[0], projection_magnitude * line_unit_vector[1])

        # calculate the perpendicular vector
        perpendicular_vector = (vector[0] - projection_vector[0], vector[1] - projection_vector[1])

        return projection_vector, perpendicular_vector

    def _handle_collision(self, intersection_point, line, angle, contact_points):
        # print(self.prev_frame_collision)
        self.rotation_velocity = (2 / self._mass * math.dist(intersection_point, self.center) ** 2) * \
                                 self._inertia * (self.velocity[0] ** 2 + self.velocity[1] ** 2) * \
                                 math.sin(angle / 2) - self.rotation_velocity

        velocity_parallel, velocity_perpendicular = self.decompose_vector(self.velocity, line)
        # print(1, self.velocity)
        if contact_points >= 2:
            self.velocity = [velocity_parallel[0] - velocity_perpendicular[0],
                             velocity_parallel[1] - velocity_perpendicular[1]]
        else:
            self.velocity = [-velocity_parallel[0] - velocity_perpendicular[0],
                             -velocity_parallel[1] - velocity_perpendicular[1]]

        if self.prev_frame_collision == 0:
            # make the bounces less beneficial
            self.velocity[0] *= 0.7
            self.velocity[1] *= 0.7
        # print(2, self.velocity)

        # print(self.center)

        if self.prev_frame_collision == 2:
            print("bum")
            self.velocity = [0, 0]
            self.acceleration = [0, 0]
            self.rotation_velocity = 0
            self.rotation_acceleration = 0
            self.center, self.angle = deepcopy(self.p_position)
        else:
            self.center, self.angle = deepcopy(self.p_position)
            self.prev_frame_collision = 3

    def check_collisions(self, lines):
        points = self.get_points()
        for line in lines:
            intersection_total = [0, 0]
            intersection_angle = 0
            intersection_number = 0
            for i in range(4):
                car_line = (points[i], points[(i + 1) % 4])

                intersection, angle = self.line_intersection(car_line, line)
                if intersection is not None:
                    intersection_total[0] += intersection[0]
                    intersection_total[1] += intersection[1]
                    intersection_angle += angle
                    intersection_number += 1

            if intersection_number > 0:
                intersection = [0, 0]
                intersection[0] = intersection_total[0] / intersection_number
                intersection[1] = intersection_total[1] / intersection_number
                angle = intersection_angle / intersection_number

                self._handle_collision(intersection, line, angle, intersection_number)
                return

        self.p_position = deepcopy((self.center, self.angle))

    def check_checkpoints(self, lines):
        points = self.get_points()
        # print(1, self.next_checkpoint, len(lines))
        if self.next_checkpoint < len(lines):
            for i in range(4):
                car_line = (points[i], points[(i + 1) % 4])

                # print(2, self.next_checkpoint, len(lines))
                intersection, angle = self.line_intersection(car_line, lines[self.next_checkpoint])
                if intersection is not None:
                    self.next_checkpoint += 1
                    return
        else:
            self.finished_checkpoints = True

    def check_finish(self, finish):
        if not self.finished_checkpoints:
            return False

        points = self.get_points()

        for i in range(4):
            car_line = (points[i], points[(i + 1) % 4])
            intersection, angle = self.line_intersection(car_line, finish)
            if intersection is not None:
                self.next_checkpoint = 0
                self.finished_checkpoints = False
                return True

        return False

    def ray_cast(self, angle, lines):
        angle += self.angle
        ray = [[0 + self.center[0], 0 + self.center[1]],
                [10 * math.cos(angle) + self.center[0], -10 * math.sin(angle) + self.center[1]]]

        end_point = None
        for line in lines:
            intersection, angle = self.line_intersection(ray, line)
            if intersection is not None:
                if end_point is None or math.dist(self.center, intersection) < math.dist(self.center, end_point):
                    end_point = intersection

        ray[1] = end_point
        return ray

    @staticmethod
    def line_intersection(line1, line2):
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        # calculate the denominator
        denominator = ((y4 - y3) * (x2 - x1)) - ((x4 - x3) * (y2 - y1))

        # check if the lines are parallel
        if denominator == 0:
            return None, None

        # calculate the numerators
        numerator1 = ((x4 - x3) * (y1 - y3)) - ((y4 - y3) * (x1 - x3))
        numerator2 = ((x2 - x1) * (y1 - y3)) - ((y2 - y1) * (x1 - x3))

        # calculate the values of t1 and t2
        t1 = numerator1 / denominator
        t2 = numerator2 / denominator

        # check if the intersection point is within the range of the line segments
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            intersection_x = x1 + (t1 * (x2 - x1))
            intersection_y = y1 + (t1 * (y2 - y1))
            angle_radians = math.atan2(y4 - y3, x4 - x3) - math.atan2(y2 - y1, x2 - x1)
            return (intersection_x, intersection_y), angle_radians
        else:
            return None, None

    # overcomplicated function for updating car physics
    def update(self, dt, tire_change, is_accelerating, breaking, reverse):
        if self.prev_frame_collision > 0:
            self.prev_frame_collision -= 1

        # print(self.center)

        if is_accelerating:
            # assuming front-wheel drive
            self.acceleration = [self._engine_force / self._mass * math.cos(self.angle + self.tire_angle),
                                 self._engine_force / self._mass * -math.sin(self.angle + self.tire_angle)]
            # assuming rear-wheel drive
            # self.acceleration = [self.engine_force / self.mass * math.cos(self.angle),
            #                      self.engine_force / self.mass * -math.sin(self.angle)]
            # distance of center of mass to the axis of rotation
            if self.tire_angle:
                axis_distance = self._length * math.sqrt(1 / 4 + 1 / (math.tan(self.tire_angle) * math.tan(self.tire_angle)))
                self.rotation_acceleration = self._engine_force * math.sin(self.tire_angle) / \
                                             (self._inertia + self._mass * axis_distance * axis_distance) * 1.5
            else:
                self.rotation_acceleration = 0
        else:
            self.acceleration = [0.0, 0.0]
            self.rotation_acceleration = 0.0

        # calculate velocity angle
        self.velocity_direction = math.atan2(-self.velocity[1], self.velocity[0])

        # calculate drag
        velocity_mag_sq = self.velocity[0] ** 2 + self.velocity[1] ** 2
        drag_force = self._mass * self._friction_coefficient + velocity_mag_sq * self._drag_coefficient + \
                     self._break_force * breaking

        # make it turn naturally
        force = self._wheel_max_force * math.sin(self.tire_angle)
        self.rotation_acceleration += force * self._length / self._inertia * (velocity_mag_sq ** 0.7)

        # introduce friction and drag
        if velocity_mag_sq > 0.001:
            self.acceleration[0] -= drag_force / self._mass * math.cos(self.velocity_direction)
            self.acceleration[1] -= drag_force / self._mass * -math.sin(self.velocity_direction)
        # stop the car completely when it's really slow (to avoid back and forth)
        elif breaking or (abs(self.acceleration[0]) < 0.01 and abs(self.acceleration[1]) < 0.01):
            self.velocity = [0.0, 0.0]

        # print(self.rotation_velocity)

        # introduce rotation friction
        # scale it with speed, tire_angle and rotation velocity
        if self.rotation_velocity > 0.001:
            self.rotation_acceleration -= drag_force / self._mass * (math.cos(self.tire_angle) + 1) * 1.2 * \
                                          abs(self.rotation_velocity)
        elif self.rotation_velocity < -0.001:
            self.rotation_acceleration += drag_force / self._mass * (math.cos(self.tire_angle) + 1) * 1.2 * \
                                          abs(self.rotation_velocity)
        # stop rotation completely if it's too slow
        else:
            if abs(self.rotation_acceleration) < 0.999:
                self.rotation_velocity = 0

        if reverse:
            self.acceleration[0] *= -0.1
            self.acceleration[1] *= -0.1

        # apply the movement
        self.center[0] += self.velocity[0] * dt
        self.center[1] += self.velocity[1] * dt
        self.velocity[0] += self.acceleration[0] * dt
        self.velocity[1] += self.acceleration[1] * dt

        self.angle += self.rotation_velocity * dt
        self.rotation_velocity += self.rotation_acceleration * dt

        # update angle of tires
        if tire_change == 0:
            if self.tire_angle > 0:
                self.tire_angle -= self._steer * dt
                self.tire_angle = max(self.tire_angle, 0)
            if self.tire_angle < 0:
                self.tire_angle += self._steer * dt
                self.tire_angle = min(self.tire_angle, 0)
        else:
            self.tire_angle += tire_change * self._steer * dt
        # cap rotation of tires at 60 deg
        self.tire_angle = max(-math.pi / 3, min(math.pi / 3, self.tire_angle))

    def get_vel(self):
        return math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

    def get_points(self):
        points = [(self._length / 2.0, self._width / 2.0),
                  (-self._length / 2.0, self._width / 2.0),
                  (-self._length / 2.0, -self._width / 2.0),
                  (self._length / 2.0, -self._width / 2.0)]
        for i in range(len(points)):
            translation = (points[i][0] * math.cos(self.angle) + points[i][1] * math.sin(self.angle) + self.center[0],
                           -points[i][0] * math.sin(self.angle) + points[i][1] * math.cos(self.angle) + self.center[1])
            points[i] = translation
        return points

    def __init__(self, center, angle):
        self._length = 1.0 / 2.5  # tiles
        self._width = 1.0 / 5.0  # tiles

        # movement constants
        self._engine_force = 4000  # Nm
        self._break_force = 3000  # N
        self._friction_coefficient = 1.2
        self._drag_coefficient = 100
        self._wheel_max_force = 5000
        self._mass = 2000
        magic_constant = 20
        self._inertia = self._mass / 12 * (self._length * self._length + self._width * self._width) * magic_constant

        # controls constants
        self._steer = 5

        # position and movement variables
        self.center = center
        self.p_position = (center, 0)
        self.angle = angle
        self.tire_angle = 0.0
        self.velocity = [0.0, 0.0]
        self.acceleration = [0.0, 0.0]
        self.rotation_velocity = 0.0
        self.rotation_acceleration = 0.0

        # collision helper variable
        self.prev_frame_collision = 0

        # gui variable
        self.velocity_direction = 0.0

        # track variables
        self.next_checkpoint = 0
        self.finished_checkpoints = False
