import asyncio
from sys import exit

from bleak import BleakClient, uuids
import keyboard

TRIANGLE = 4
CROSS = 16
SQUARE = 32
CIRCLE = 8
SELECT = 2
START = 1

active_keys = []


def hooke(e):
    if e.event_type == 'down':
        if e.name not in active_keys:
            active_keys.append(e.name)
        elif e.name == 'esc':
            exit(0)  # Successful exit
    elif e.event_type == 'up' and e.name in active_keys:
        active_keys.remove(e.name)


keyboard.hook(hooke, suppress=True)


# Replace with the MAC address of your Raspberry Pi Pico W
pico_address = "28:CD:C1:0E:9D:2F"  # Update this with your Pico W's address

# Service UUID (0x1848) - but we need to normalize it to 128-bit UUID
SERVICE_UUID = uuids.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
WRITE_CHARACTERISTIC_UUID = uuids.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E") # Central writes here
READ_CHARACTERISTIC_UUID = uuids.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # Central reads here

def pack_prepare(active_keys):
    null_pack = [b'\xff', b'\x01', b'\x02', b'\x01', b'\x02', b'\x00', b'\x00', b'\x00']
    null_pack[5] = 0  # keys
    null_pack[6] = 0  # vector of direction (speed: -7..+7; angle: 0..360 degrees)

    if "r" in active_keys:
        null_pack[5] = null_pack[5] | TRIANGLE
    if "w" in active_keys:
        if "a" in active_keys:
            null_pack[6] = null_pack[6] | 9
        elif "d" in active_keys:
            null_pack[6] = null_pack[6] | 3
        else:
            null_pack[6] = null_pack[6] | 6
    elif "s" in active_keys:
        if "a" in active_keys:
            null_pack[6] = null_pack[6] | 15
        elif "d" in active_keys:
            null_pack[6] = null_pack[6] | 21
        else:
            null_pack[6] = null_pack[6] | 18
    elif "a" in active_keys:
        null_pack[6] = null_pack[6] | 24
    elif "d" in active_keys:
        null_pack[6] = null_pack[6] | 12
    if len(active_keys) > 0:
        null_pack[6] = ((null_pack[6] << 3) | 7)
    null_pack[5] = null_pack[5].to_bytes(1, 'big')
    null_pack[6] = null_pack[6].to_bytes(1, 'big')
    print(null_pack)
    res = b''.join(null_pack)
    print(res)
    return res


async def send_data_task(client):
    """Send data to the peripheral device."""
    while True:
        message = f"{active_keys}".encode("utf-8")
        # print(f"Central sending: {message}")
        await client.write_gatt_char(WRITE_CHARACTERISTIC_UUID, pack_prepare(active_keys))
        await asyncio.sleep(0.5)

async def receive_data_task(client):
    """Receive data from the peripheral device."""
    while True:
        try:
            # print("Central waiting for data from peripheral...")
            response = await client.read_gatt_char(READ_CHARACTERISTIC_UUID)
            print(f"Central received: {response.decode('utf-8')}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

async def connect_and_communicate(address):
    """Connect to the peripheral and manage data exchange."""
    print(f"Connecting to {address}...")

    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")

        # Create tasks for sending and receiving data
        tasks = [
            asyncio.create_task(send_data_task(client)),
            asyncio.create_task(receive_data_task(client)),

        ]
        await asyncio.gather(*tasks)

# Run the connection and communication
loop = asyncio.get_event_loop()
loop.run_until_complete(connect_and_communicate(pico_address))