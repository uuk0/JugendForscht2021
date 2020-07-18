import math
import typing

import pyglet
from pyglet.gl import *

from pyglet.window import key


class IPointGenerator:
    def iteratePositions(self) -> typing.Iterator:
        raise NotImplementedError()

    def getPositionForPosition(self, position) -> typing.Tuple[float, float, float]:
        raise NotImplementedError()


class Window(pyglet.window.Window):
    """
    This is an framework around drawing 3d graphs of mathematical functions
    Use WSAD to move around and arrow keys to rotate

    Create an new Window for loading:
        Window(<IPointGenerator-instance>)
    Start main loop:
        <window-instance>.mainloop() or pyglet.app.run()

    Example:
        Window(FunctionBasedGenerator(lambda x, y: x * y)).mainloop()
    """

    def __init__(self, generator: IPointGenerator, count_per_tick=10, start_direct=True, color=(255, 255, 255)):
        # todo: add option for background color
        super().__init__(caption="Jugend Forscht")
        self.positions = generator.iteratePositions()
        self.generator = generator
        self.batch = pyglet.graphics.Batch()
        pyglet.clock.schedule_interval(self.do_next, .1)
        self.running = start_direct
        self.position = (1.5, 2, 1.5)
        self.rotation = (-45, -45)
        self.elements = set()
        self.count_per_tick = count_per_tick
        self.strafe = [0, 0]
        self.r_strafe = [0, 0]
        self.color = color

    def on_draw(self):
        # todo: add some info label
        self.clear()
        self.set_3d()
        self.batch.draw()

    def do_next(self, dt=0):
        d = dt * 5
        dx, dy, dz = self.get_motion_vector()
        x, y, z = self.position
        self.position = (x + dx * d, y + dy * d, z + dz * d)
        self.rotate_view(self.r_strafe[1] * dt * 40, -self.r_strafe[0] * dt * 40)
        if not self.running: return
        positions = []
        # todo: collect optional colors
        for _ in range(self.count_per_tick):
            try:
                p = next(self.positions)
                positions.append(self.generator.getPositionForPosition(p))
            except StopIteration:
                break
        self.elements.add(self.batch.add(len(positions), GL_POINTS, None, ("v3f", sum(positions, tuple())),
                                         ("c{}B".format(len(self.color)), self.color*len(positions))))

    def changeTargetFunction(self, generator: IPointGenerator, remove_old=True):
        self.positions = generator.iteratePositions()
        self.generator = generator
        if remove_old:
            [e.delete() for e in self.elements]
            self.elements.clear()

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

        elif symbol == key.R:
            self.position = (1.5, 2, 1.5)
            self.rotation = (-45, -45)
        elif symbol == key.ENTER:
            self.running = not self.running

        # todo: add screenshot tool

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


class FunctionBasedGenerator(IPointGenerator):
    def __init__(self, function: typing.Callable, size=(100, 100, 10, 10)):
        self.function = function
        self.size = size

    def iteratePositions(self) -> typing.Iterator:
        for x in range(-self.size[0] // 2, self.size[0] // 2 + 1):
            for y in range(-self.size[1] // 2, self.size[1] // 2 + 1):
                yield x / self.size[2], y / self.size[3]

    def getPositionForPosition(self, position) -> typing.Tuple[float, float, float]:
        x, y = position
        return x, self.function(*position), y


# Window(FunctionBasedGenerator(lambda x, z: abs(complex(x, z) ** 2), size=(100, 100, 10, 10)), count_per_tick=100).mainloop()
# Window(FunctionBasedGenerator(lambda x, z: (complex(x, z) ** 2).real, size=(100, 100, 10, 10)), count_per_tick=100).mainloop()
# Window(FunctionBasedGenerator(lambda x, z: (complex(x, z) ** 2).imag, size=(100, 100, 10, 10)), count_per_tick=100).mainloop()
# Window(FunctionBasedGenerator(lambda x, y: abs(complex(x, y) * (complex(x, y) ** 2 + 1)), size=(100, 100, 10, 10)), count_per_tick=100).mainloop()


class MandelbrotGenerator(IPointGenerator):
    def __init__(self, size=(100, 100, 10, 10), max_iterations=400, stretch_factor=100, power=2, outer_limit=2):
        self.size = size
        self.max_iterations = max_iterations
        self.stretch_factor = stretch_factor
        self.power = power
        self.outer_limit = outer_limit

    def iteratePositions(self) -> typing.Iterator:
        for x in range(-self.size[0] // 2, self.size[0] // 2 + 1):
            for y in range(-self.size[1] // 2, self.size[1] // 2 + 1):
                yield x / self.size[2], y / self.size[3]

    def getPositionForPosition(self, position) -> typing.Tuple[float, float, float]:
        v = complex(0, 0)
        x, y = position
        t = complex(x, y)
        for iteration in range(self.max_iterations):
            v = v ** self.power + t
            if abs(v) > self.outer_limit:
                return x, 1 / iteration * self.stretch_factor if iteration != 0 else 10, y
        return x, 0, y


Window(MandelbrotGenerator(size=(800, 800, 200, 200), outer_limit=5, stretch_factor=200), count_per_tick=1000, start_direct=False).mainloop()



