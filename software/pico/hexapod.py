import asyncio
import time
import sys

from machine import Pin, I2C
import math

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
from servo.servo import Servos


def speed_divider(multiplier=1):
    max_speed = 360  # 360ms for 180 degrees rotation. From the servo specification
    rotation_range = 180
    zero_speed = max_speed / 2  # zero speed
    result_speed = (zero_speed * multiplier) / rotation_range
    return result_speed


class MotorDriver:
    max_speed = 360  # 360ms for 180 degrees rotation. From the servo specification
    rotation_range = 180

    def __init__(self, driver_addr) -> None:
        self.driver_addr = driver_addr
        self.driver = Servos(i2c=i2c, address=driver_addr)


class MotorSet:
    def __init__(self, driver, channel_id) -> None:
        self.driver = driver
        self.id = channel_id

    def rotation(self, angle):
        self.driver.driver.position(index=self.id, degrees=angle)
        # print(f"channel_id:  {self.id}\t rotation angle:  {angle}")
        time.sleep_us(500)
        #         return [f"motor_id {self.id}", angle]
        pass


class Leg:
    def __init__(self, leg_id, motor_a: MotorSet, motor_b: MotorSet, motor_c: MotorSet, angle: int) -> None:
        self.road_map = []
        self.direction = 1
        self.rotation = 0
        self.leg_id = leg_id
        self.motor_a = motor_a
        self.motor_b = motor_b
        self.motor_c = motor_c
        self.deviation_a = 0
        self.deviation_b = 0
        self.deviation_c = 0
        self.parts = 15  # quantity of steps
        self.X_Rest = 0  # zero position at x-axis
        self.Y_Rest = 50  # zero position at y-axis
        self.Z_Rest = -30  # zero position at z-axis
        self.J2L = 50  # length of arm in mm from body to the middle
        self.J3L = 70  # length of arm in mm from middle to the ground
        self.J3_rest = math.acos(((self.J2L * self.J2L) + (self.J3L * self.J3L) - (
                (self.Y_Rest * self.Y_Rest) + (self.Z_Rest * self.Z_Rest))) / (2 * self.J2L * self.J3L)) * (
                               180 / math.pi)
        self.old_coordinate = {"X": 0, "Y": 0, "Z": 0}
        self.angle = angle

    def drive(self):
        for q in self.road_map:
            x = q[0]
            y = q[1]
            w = q[2]
            self.motor_a.rotation(x)
            self.motor_b.rotation(y)
            self.motor_c.rotation(w)
            yield {f"{self.leg_id}:a": x,
                   f"{self.leg_id}:b": y,
                   f"{self.leg_id}:c": w}

    def _cartesian_move(self, X, Y, Z, yaw):
        angle = self.angle + yaw
        # OFFSET TO REST POSITION
        Z = -Z
        Z += self.Z_Rest
        Y += self.Y_Rest

        if not self.rotation:
            if self.leg_id in [1, 2, 3]:
                X = -X

            if self.leg_id not in [2, 5]:
                X = X + X * math.cos(angle)

            Y = Y + X * math.sin(angle)

        # CALCULATE INVERSE KINEMATIC SOLUTION
        J1 = math.atan(X / Y) * (180 / math.pi)
        H = math.sqrt((Y * Y) + (X * X))
        L = math.sqrt((H * H) + (Z * Z))
        J3 = math.acos(((self.J2L * self.J2L) + (self.J3L * self.J3L) - (L * L)) / (2 * self.J2L * self.J3L)) * (
                180 / math.pi)
        J3_result = 2 * self.J3_rest - J3
        B = math.acos(((L * L) + (self.J2L * self.J2L) - (self.J3L * self.J3L)) / (2 * L * self.J2L)) * (180 / math.pi)
        A = math.atan(Z / H) * (180 / math.pi)  # BECAUSE Z REST IS NEGATIVE, THIS RETURNS A NEGATIVE VALUE
        J2 = (B + A)  # BECAUSE 'A' IS NEGATIVE AT REST WE NEED TO INVERT '-' TO '+'
        if self.leg_id in [1, 2, 3]:  # left side
            return J1 + 90 + self.deviation_a, 90 + J2 + self.deviation_b, 90 + J3_result + self.deviation_c
        else:  # right side
            return J1 + 90 + self.deviation_a, 90 - J2 + self.deviation_b, 90 - J3_result + self.deviation_c

    def wave_move(self, X, Y, Z, yaw):
        self.road_map = []

        part = 180 / self.parts
        X_part = (self.old_coordinate["X"] - X) / self.parts
        Y_part = (self.old_coordinate["Y"] - Y) / self.parts

        for i in range(self.parts + 1):
            _x = self.old_coordinate["X"] - X_part * i
            _y = self.old_coordinate["Y"] + Y_part * i
            if self.old_coordinate["X"] > X:
                _z = Hexapod.up_ * math.sin(math.radians(i * part))
            else:
                _z = Z
            self.road_map.append(self._cartesian_move(_x,
                                                      _y,
                                                      _z,
                                                      yaw))
        self.old_coordinate = {"X": X, "Y": Y, "Z": Z}


class Hexapod:
    h_step = 15
    up_ = -15

    def __init__(self) -> None:
        self.motor_angles = {}
        self._direction = 1
        self._rotation = 0
        self.angle = 30
        try:
            self.driver_1 = MotorDriver(0x40)
        except Exception as e:
            self.driver_1 = None
            print(f"Servo driver 1: {e}")
        try:
            self.driver_2 = MotorDriver(0x41)
        except Exception as e:
            self.driver_2 = None
            print(f"Servo driver 2: {e}")
        if self.driver_1 is None or self.driver_2 is None:
            sys.exit(-1)

        self.speed_multiplier = 0
        self.roll = 0  # kren
        self.pitch = 0  # tangaj
        self.yaw = 0  # kyrs\

        self.leg_1 = Leg(1, MotorSet(self.driver_1, 4), MotorSet(self.driver_1, 5), MotorSet(self.driver_1, 6),
                         angle=- self.angle)  # ok
        self.leg_1.deviation_a = 0
        self.leg_1.deviation_b = -15
        self.leg_1.deviation_c = -20

        self.leg_2 = Leg(2, MotorSet(self.driver_1, 8), MotorSet(self.driver_1, 9), MotorSet(self.driver_1, 10),
                         angle=0)  # ok
        self.leg_2.deviation_a = 7
        self.leg_2.deviation_b = -23
        self.leg_2.deviation_c = -14

        self.leg_3 = Leg(3, MotorSet(self.driver_1, 12), MotorSet(self.driver_1, 13), MotorSet(self.driver_1, 14),
                         angle=self.angle)  # ok
        self.leg_3.deviation_a = 0
        self.leg_3.deviation_b = -23
        self.leg_3.deviation_c = -8

        self.leg_4 = Leg(4, MotorSet(self.driver_2, 15), MotorSet(self.driver_2, 14), MotorSet(self.driver_2, 13),
                         angle=self.angle)  # ok
        self.leg_4.deviation_a = 10
        self.leg_4.deviation_b = 20
        self.leg_4.deviation_c = -5

        self.leg_5 = Leg(5, MotorSet(self.driver_2, 11), MotorSet(self.driver_2, 10), MotorSet(self.driver_2, 9),
                         angle=0)  # ok
        self.leg_5.deviation_a = 10
        self.leg_5.deviation_b = 5
        self.leg_5.deviation_c = 7

        self.leg_6 = Leg(6, MotorSet(self.driver_2, 7), MotorSet(self.driver_2, 6), MotorSet(self.driver_2, 5),
                         angle=- self.angle)  # ok
        self.leg_6.deviation_a = 0
        self.leg_6.deviation_b = 17
        self.leg_6.deviation_c = 25

    def _step_left(self, angle):
        if self.speed_multiplier < 0:
            step = 0
        else:
            step = self.h_step*self.direction

        self.leg_1.wave_move(step, 0, 0, angle)
        self.leg_5.wave_move(step, 0, 0, angle)
        self.leg_3.wave_move(step, 0, 0, angle)

        self.leg_4.wave_move(-step, 0, 0, angle)
        self.leg_2.wave_move(-step, 0, 0, angle)
        self.leg_6.wave_move(-step, 0, 0, angle)

    def _step_right(self, angle):
        if self.speed_multiplier < 0:
            step = 0
        else:
            step = self.h_step*self.direction

        self.leg_1.wave_move(-step, 0, 0, angle)
        self.leg_5.wave_move(-step, 0, 0, angle)
        self.leg_3.wave_move(-step, 0, 0, angle)

        self.leg_4.wave_move(step, 0, 0, angle)
        self.leg_2.wave_move(step, 0, 0, angle)
        self.leg_6.wave_move(step, 0, 0, angle)

    def _speed(self, speed):
        self.speed_multiplier = speed

    def _move(self):
        l2 = self.leg_2.drive()
        l1 = self.leg_1.drive()
        l3 = self.leg_3.drive()
        l4 = self.leg_4.drive()
        l5 = self.leg_5.drive()
        l6 = self.leg_6.drive()
        while True:
            try:
                next(l1)
                next(l2)
                next(l3)
                next(l4)
                next(l5)
                next(l6)
            except Exception as e:
                print(e)
                break

    async def move(self, speed=1, angle=0):
        self._speed(speed)
        if speed != 0:
            self._step_left(angle)
            self._move()
            await asyncio.sleep(0.1)

            self._step_right(angle)
            self._move()
            await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(0.5)
            print("idle")

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, _direction):
        self.leg_1.direction = _direction
        self.leg_2.direction = _direction
        self.leg_3.direction = _direction
        self.leg_4.direction = _direction
        self.leg_5.direction = _direction
        self.leg_6.direction = _direction
        self._direction = _direction

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, _rotation):
        self.leg_1.rotation = _rotation
        self.leg_2.rotation = _rotation
        self.leg_3.rotation = _rotation
        self.leg_4.rotation = _rotation
        self.leg_5.rotation = _rotation
        self.leg_6.rotation = _rotation

        self._rotation = _rotation


async def main():
    _hex = Hexapod()
    _hex.rotation = 0
    _hex.direction = 1
    print("move")
    await _hex.move(speed=-1, angle=0)
    print("sleep")
    time.sleep(3)

    while 1:
        await  _hex.move(speed=1, angle=0)
        time.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
