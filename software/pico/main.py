import aioble
import bluetooth
from machine import ADC
import asyncio

from hexapod import Hexapod
from ble_uart import BLEUART

# ADC Channel 4 reads the temperature sensor
sensor_temp = ADC(4)
conversion_factor = 3.3 / 65535  # Conversion factor for ADC reading to voltage

TRIANGLE = 4
CROSS = 16
SQUARE = 32
CIRCLE = 8
SELECT = 2
START = 1


# Function to read the internal temperature
def read_temperature():
    raw_value = sensor_temp.read_u16()
    voltage = raw_value * conversion_factor
    temperature = 27 - (voltage - 0.706) / 0.001721
    return temperature


# state variables
message_count = 0

# Init HexaPod
print("Init Hexapod")
_hex = Hexapod()
_hex.move(speed=0, angle=0)
speed = 0
angle = 0


async def hex_move():
    global speed, angle
    while True:
        await _hex.move(speed, angle)
        await asyncio.sleep(0)


async def run_peripheral_mode():
    ble = bluetooth.BLE()
    uart = BLEUART(ble)

    def on_rx():
        global speed, angle, TRIANGLE
        msg = uart.read()
        if b'\xff\x01\x02\x01\x02' in msg:
            print('Joystic Mode')
        if b'\xff\x01\x01\x01\x02' in msg:
            print('Digital Mode is NOT SUPPORTED')
            return
        try:
            btn = msg[5]
            if btn & TRIANGLE:
                print("TRIANGLE is pressed")
                _hex.rotation = 1
            else:
                _hex.rotation = 0
            
            radius_n_angle = msg[6]
            speed = radius_n_angle & 0x07
            angle = -((radius_n_angle >> 3) * 15 - 90)

            print("buttons: ", btn, "radius_n_angle: ", speed, angle)
        except Exception:
            print(msg)

    uart.irq(handler=on_rx)

    try:
        while True:
            await hex_move()
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass

    uart.close()


asyncio.run(run_peripheral_mode())
