import math
import pygame
from pygame.locals import *


def truncate(x):
    if x >= 0:
        return math.floor(x)
    if x < 0:
        return math.ceil(x)


class Circuit:

    def __init__(self, checkpoints, nb_laps):
        self.checkpoints = checkpoints
        self.nb_checkpoints = len(self.checkpoints)
        self.nb_laps = nb_laps
        self.end = False
        self.length = self.compute_length()

    def compute_length(self):
        d = 0
        for i in range(len(self.checkpoints) - 1):
            d += self.checkpoints[i].distance(self.checkpoints[i+1])

        return d

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def squared_distance(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def distance(self, other):
        return math.sqrt(self.squared_distance(other))

    def closest(self, a, b):
        da = b.y - a.y
        db = a.x - b.x
        c1 = da * a.x + db * a.y
        c2 = -db * self.x + da * self.y
        det = da * da + db * db
        cx = 0
        cy = 0

        if det != 0:
            cx = (da * c1 - db * c2) / det
            cx = (da * c2 + db * c1) / det
        else:
            cx = self.x
            cy = self.y

        return Point(cx, cy)


class Unit(Point):

    def __init__(self, x, y, identifier, r, vx, vy):
        Point.__init__(self, x, y)
        self.id = identifier
        self.r = r
        self.vx = vx
        self.vy = vy

    def collision(self, other):
        dist = self.squared_distance(other)
        sr = (self.r + other.r) ** 2

        if dist < sr:
            return Collision(self, other, 0)

        if (self.vx == other.vx) and (self.vy == other.vy):
            return None

        x = self.x - other.y
        y = self.y - other.y
        myp = Point(x, y)
        vx = self.vx - other.vx
        vy = self.vy - other.vy
        up = Point(0, 0)

        p = up.closest(myp, Point(x + vx, y + vy))

        pdist = up.squared_distance(p)

        mypdist = myp.squared_distance(p)

        if pdist < sr:
            length = math.sqrt(vx * vx + vy * vy)
            backdist = math.sqrt(sr - pdist)
            p.x = p.x - backdist * (vx / length)
            p.y = p.y - backdist * (vy / length)

            if myp.squared_distance(p) > mypdist:
                return None

            pdist = p.distance(myp)

            if pdist > length:
                return None

            t = pdist / length

            return Collision(self, other, t)

        return None

    def bounceWithCheckpoint(self, cp, circuit):

        self.nextCheckPointId = (cp.number + 1) % circuit.nb_checkpoints
        if self.nextCheckPointId == 1:
            self.lap += 1
        if self.lap > circuit.nb_laps:
            self.win = True
        self.score += self.timeout
        self.timeout = 100

    def bounce(self, other, circuit):

        if isinstance(other, Checkpoint):
            self.bounceWithCheckpoint(other, circuit)

        else:
            if self.shield:
                m1 = 10
            else:
                m1 = 1
            if other.shield:
                m2 = 10
            else:
                m2 = 1
            mcoeff = (m1 + m2) / (m1 * m2)

            nx = self.x - other.x
            ny = self.y - other.y

            nxnysquare = nx ** 2 + ny ** 2

            dvx = self.vx - other.vx
            dvy = self.vy - other.vy
            product = nx * dvx + ny * dvy
            fx = (nx * product) / (nxnysquare * mcoeff)
            fy = (ny * product) / (nxnysquare * mcoeff)

            self.vx -= fx / m1
            self.vy -= fy / m1
            other.vx += fx / m2
            other.vy += fy / m2

            impulse = math.sqrt(fx ** 2 + fy ** 2)

            if impulse < 120:
                fx = fx * 120 / impulse
                fy = fy * 120 / impulse

            self.vx -= fx / m1
            self.vy -= fy / m1
            other.vx += fx / m2
            other.vy += fy / m2


class Collision:
    def __init__(self, a: Unit, b: Unit, t):
        self.a = a
        self.b = b
        self.t = t


class Geometry(Unit):
    def __init__(self, imgPath, width=128, height=128):
        self.image = pygame.image.load(imgPath)
        # self.image = pygame.transform.scale(self.image, (int(width), int(height)))
        self.width = width
        self.height = height
        self.visible = True

    def setVisible(self, value):
        self.visible = value

    def getCoordinates(self):
        return self.x - self.width // 2, self.y - self.height // 2


class Pod(Geometry):

    def __init__(
            self,
            x: int, y: int, identifier: int, angle: float,
            nextCheckPointId: int, checked: bool,
            timeout: int, partner, shield: bool,
            imgPath: str, width, height
    ):

        Unit.__init__(self, x, y, identifier, r=400, vx=0, vy=0)
        Geometry.__init__(self, imgPath, width, height)
        self.angle = angle
        self.nextCheckPointId = nextCheckPointId
        self.checked = checked
        self.timeout = timeout
        self.partner = partner
        self.shield = shield

        self.baseImage = self.image
        self.image = pygame.transform.rotate(self.baseImage, self.angle * 180.0 / math.pi)
        self.target_pos = None
        self.win = False
        self.lap = 1
        self.score = 0

    def getAngle(self, p: Point):

        d = self.distance(p)
        dx = (p.x - self.x) / d
        dy = (p.y - self.y) / d
        a = math.acos(dx) * 180 / math.pi

        if (dy < 0):
            a = 360 - a

        return a

    def diffAngle(self, p: Point):

        a = self.getAngle(p)
        if self.angle <= a:
            right = a - self.angle
        else:
            right = 360 - self.angle + a

        if self.angle >= a:
            left = self.angle - a
        else:
            left = 360 + self.angle - a

        if right < left:
            return right
        else:
            return -left

    def rotate_angle(self, a):

        if a > 18:
            a = 18
        elif a < -18:
            a = -18

        self.angle += a

        if self.angle >= 360:
            self.angle = self.angle - 360

        elif self.angle < 0:
            self.angle = self.angle + 360

        self.image = pygame.transform.rotate(self.baseImage, -self.angle)

    def rotate(self, p: Point):

        a = self.diffAngle(p)

        if a > 18:
            a = 18
        elif a < -18:
            a = -18

        self.angle += a

        if self.angle >= 360:
            self.angle = self.angle - 360

        elif self.angle < 0:
            self.angle = self.angle + 360

        self.image = pygame.transform.rotate(self.baseImage, -self.angle)

    def boost(self, thrust: int):

        if self.shield:
            return 0

        ra = self.angle * math.pi / 180

        self.vx += math.cos(ra) * thrust
        self.vy += math.sin(ra) * thrust

    def move(self, t):

        self.x += self.vx * t
        self.y += self.vy * t

    def end(self):

        self.x = round(self.x)
        self.y = round(self.y)
        self.vx = truncate(self.vx * 0.85)
        self.vy = truncate(self.vy * 0.85)
        self.timeout -= 1

    def play(self, p: Point, thrust: int):
        self.rotate(p)
        self.boost(thrust)
        self.move(1.0)
        self.end()


class Checkpoint(Geometry):
    def __init__(self, x: int, y: int, imgPath, number=0, width=200, height=200):
        Unit.__init__(self, x, y, number, r=600, vx=0, vy=0)
        Geometry.__init__(self, imgPath, width, height)
        self.number = number

    def setNumber(self, number):
        self.number = number


def play(pods, circuit):
    t = 0
    previous_col = None
    while t < 1:
        firstCollision = None

        for i in range(len(pods)):
            for j in range(i + 1, len(pods)):
                col = pods[i].collision(pods[j])

                if (
                        (col is not None) and
                        (col.t + t < 1) and
                        (
                                (firstCollision is None) or (col.t < firstCollision.t)
                        )
                ):
                    firstCollision = col
            col = pods[i].collision(circuit.checkpoints[pods[i].nextCheckPointId])

            if (
                    (col is not None) and
                    (col.t + t < 1) and
                    (
                            (firstCollision is None) or (col.t < firstCollision.t)
                    )
            ):
                firstCollision = col

        if (previous_col is not None) and (firstCollision is not None):
            if isinstance(previous_col.a, Pod) and isinstance(previous_col.b, Pod):
                if isinstance(firstCollision.a, Pod) and isinstance(firstCollision.b, Pod):
                    if (previous_col.a.id == firstCollision.a.id) and (previous_col.b.id == firstCollision.b.id):
                        if previous_col.t == 0:
                            firstCollision = None

        if firstCollision is None:
            for i in range(len(pods)):
                pods[i].move(1 - t)

            t = 1
        else:
            for i in range(len(pods)):
                pods[i].move(firstCollision.t)
            firstCollision.a.bounce(firstCollision.b, circuit)
            t += firstCollision.t

        previous_col = firstCollision

    for i in range(len(pods)):
        pods[i].end()


def run(pods, circuit, targets, thrusts):
    for i in range(len(pods)):
        pods[i].rotate(Point(targets[i][0], targets[i][1]))
        pods[i].boost(thrusts[i])

    play(pods, circuit)

def run_angles(pods, circuit, angles, thrusts):
    for i in range(len(pods)):
        pods[i].rotate_angle(angles[i])
        pods[i].boost(thrusts[i])

    play(pods, circuit)
