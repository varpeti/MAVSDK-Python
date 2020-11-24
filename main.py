#!/usr/bin/env python3

import asyncio

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

localDronePos = \
    {
        'north': 0.0,
        'east': 0.0,
        'down': 0.0,
        'yaw': 0.0
    }


def moveDrone(x, z, y, d):
    localDronePos['north'] += x
    localDronePos['east'] += z
    localDronePos['down'] += y
    localDronePos['yaw'] += d

    return PositionNedYaw(localDronePos['north'], localDronePos['east'], localDronePos['down'], localDronePos['yaw'])


async def readStatus(drone):
    async for st in drone.telemetry.status_text():
        print(f"Status: {st.text}")


async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone with UUID: {state.uuid}")
            break

    asyncio.create_task(readStatus(drone))

    # Checking if Global Position Estimate is ok
    async for global_lock in drone.telemetry.health():
        if global_lock.is_global_position_ok:
            print("Global position state is good enough for flying.")
            break

    print("Arming")
    await drone.action.arm()

    print('Take off')
    await drone.action.takeoff()
    await asyncio.sleep(5)

    print("Setting initial setpoint")
    await drone.offboard.set_position_ned(moveDrone(0.0, 0.0, -5.0, 0.0))

    print("Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("Disarming")
        await drone.action.disarm()
        return

    '''
    print("Go North 10m")
    await drone.offboard.set_position_ned(moveDrone(2.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(5)
    print("Go East 10m and turn 90°")
    await drone.offboard.set_position_ned(moveDrone(0.0, 2.0, 0.0, 90.0))
    await asyncio.sleep(5)
    print("Go South 10m and turn 90°")
    await drone.offboard.set_position_ned(moveDrone(-2.0, 0.0, 0.0, 90.0))
    await asyncio.sleep(5)
    print("Go West 10m and turn 90°")
    await drone.offboard.set_position_ned(moveDrone(0.0, -2.0, 0.0, 90.0))
    await asyncio.sleep(5)
    print("Face North again")
    await drone.offboard.set_position_ned(moveDrone(0.0, 0.0, 0.0, 90.0))
    await asyncio.sleep(5)
    '''

    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, -1, 0))
    await asyncio.sleep(20)

    print("Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")

    print("Return HOME")
    await drone.action.return_to_launch()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
