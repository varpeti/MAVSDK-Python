#!/usr/bin/env python3

import asyncio

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw
from typing import List

from Astar import Pos, Astar
from Octree import Vector3, Octree
from Draw import Draw

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


async def run(path: List[Pos]):
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

    for p in path:
        print("Goto:", p)
        await drone.offboard.set_position_ned(PositionNedYaw(p.x, p.y, p.z, 0))
        await asyncio.sleep(5)  # TODO read our pos, adjust, then move on

    print("Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")

    print("Return HOME")
    await drone.action.return_to_launch()


def loadMap(fileName: str, root: Octree):
    def mine(line: str, root: Octree):
        data = line.split(' ')
        pos = Vector3(float(data[0]), float(data[1]), float(data[2]))
        size = Vector3(float(data[3]), float(data[4]), float(data[5]))
        root.setValue(pos, size, "Obstacle")

    f = open(fileName, "r")
    while f:
        line = f.readline()
        if line == "": break
        mine(line, root)
    f.close()


if __name__ == "__main__":
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Vector3(0.0, 0.0, -32.0), Vector3(32.0, 32.0, 32.0), "Air")
    loadMap("obstacles/obstacles.map",root)
    start = Pos(0.0, 0.0, 0.0)
    goal = Pos(6.0, 0.2, -2.0)
    path = Astar(start, goal, root)
    draw = Draw(Vector3(-32.0, -32.0, 0.0), Vector3(32.0, 32.0, -64.0))
    draw.showPath(path)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(path))
