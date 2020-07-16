import math
import typing

import pyglet
from pyglet.gl import *

from pyglet.window import key


def iterator(size_x, size_y, factor_x, factor_y):
    for x in range(-size_x // 2, size_x // 2 + 1):
        for y in range(-size_y // 2, size_y // 2 + 1):
            yield x / factor_x, y / factor_y


class Window(pyglet.window.Window):
    def __init__(self, function: typing.Callable, size=(100, 100, 100, 100), count_per_tick=3):
        super().__init__(caption="Jugend Forscht")
        self.positions = iterator(*size)
        self.function = function
        self.batch = pyglet.graphics.Batch()
        pyglet.clock.schedule_interval(self.do_next, .1)
        self.position = (1.5, 2, 1.5)
        self.rotation = (-45, -45)
        self.elements = set()
        self.count_per_tick = count_per_tick
        self.strafe = [0, 0]
        self.r_strafe = [0, 0]

    def on_draw(self):
        self.clear()
        self.set_3d()
        self.batch.draw()

    def do_next(self, dt=0):
        d = dt * 5
        dx, dy, dz = self.get_motion_vector()
        x, y, z = self.position
        self.position = (x + dx * d, y + dy * d, z + dz * d)
        self.rotate_view(self.r_strafe[1] * dt * 10, -self.r_strafe[0] * dt * 10)
        for _ in range(self.count_per_tick):
            try:
                x, y = next(self.positions)
                v = self.function(x, y)
                self.elements.add(self.batch.add(1, GL_POINTS, None, ("v3f", (x, v, y)), ("c3B", (255, 255, 255))))
            except StopIteration:
                return

    def set_3d(self):
        """
        Configure OpenGL to draw in 3d.
        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def mainloop(self):
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W: self.strafe[0] = -1
        elif symbol == key.S: self.strafe[0] = 1
        elif symbol == key.A: self.strafe[1] = -1
        elif symbol == key.D: self.strafe[1] = 1

        elif symbol == key.UP: self.r_strafe[0] = -1
        elif symbol == key.DOWN: self.r_strafe[0] = 1
        elif symbol == key.LEFT: self.r_strafe[1] = -1
        elif symbol == key.RIGHT: self.r_strafe[1] = 1

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W or symbol == key.S: self.strafe[0] = 0
        if symbol == key.A or symbol == key.D: self.strafe[1] = 0
        if symbol == key.UP or symbol == key.DOWN: self.r_strafe[0] = 0
        if symbol == key.LEFT or symbol == key.RIGHT: self.r_strafe[1] = 0

    def get_motion_vector(self) -> tuple:
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            m = math.cos(y_angle)
            dy = math.sin(y_angle)
            if self.strafe[1]:
                # Moving left or right.
                dy = 0.0
                m = 1
            if self.strafe[0] > 0:
                # Moving backwards.
                dy *= -1
            # When you are flying up or down, you have less left and right
            # motion.
            dx = math.cos(x_angle) * m
            dz = math.sin(x_angle) * m
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def rotate_view(self, dx, dy):
        m = 0.15
        x, y = self.rotation
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        self.rotation = (x, y)


# Window(lambda x, z: abs(complex(x, z) ** 2), count_per_tick=100, size=(100, 100, 10, 10)).mainloop()
# Window(lambda x, z: (complex(x, z) ** 2).real, count_per_tick=100, size=(100, 100, 10, 10)).mainloop()
# Window(lambda x, z: (complex(x, z) ** 2).imag, count_per_tick=100, size=(100, 100, 10, 10)).mainloop()


