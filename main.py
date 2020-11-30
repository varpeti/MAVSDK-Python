#!/usr/bin/env python3

import asyncio
from random import random

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw
from typing import List

from Astar import Astar
from Octree import Octree
from Pos import Pos
from Draw import Draw

async def readStatus(drone):
    async for st in drone.telemetry.status_text():
        print(f"Status: {st.text}")


async def getPosition(drone):
    async for p in drone.telemetry.position_velocity_ned():
        return Pos(p.position.north_m, p.position.east_m, p.position.down_m)


async def closeEnough(p1: Pos, p2: Pos, close):
    return abs(p1.x - p2.x) < close and \
           abs(p1.y - p2.y) < close and \
           abs(p1.z - p2.z) < close


isCollisionAlert = 0


async def receiveMessageHackedIntoGPS(drone):
    global isCollisionAlert
    async for g in drone.telemetry.gps_info():
        if g.num_satellites > 100:
            isCollisionAlert = g.num_satellites
        else:
            isCollisionAlert = 0


async def run(path: List[Pos]):
    global isCollisionAlert
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone with UUID: {state.uuid}")
            break

    asyncio.create_task(readStatus(drone))
    asyncio.create_task(receiveMessageHackedIntoGPS(drone))

    # Checking if Global Position Estimate is ok
    async for global_lock in drone.telemetry.health():
        if global_lock.is_global_position_ok:
            print("Global position state is good enough for flying.")
            break

    print("Arming")
    await drone.action.arm()

    print("Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    print("Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    cd = 1.0
    wasAlert = False
    for p in path:
        print("Goto:", p)
        await drone.offboard.set_position_ned(PositionNedYaw(p.x, p.y, p.z, 0))

        while True:
            pos = await getPosition(drone)
            if await closeEnough(pos, p, 0.25): break

            # TODO: better collision avoidance
            if isCollisionAlert > 0:
                wasAlert = True
                fuzzA = random()*(cd*2.0)-cd
                fuzzB = random()*(cd*2.0)-cd
                if isCollisionAlert == 100:
                    await drone.offboard.set_position_ned(PositionNedYaw(pos.x+cd, p.y+fuzzA, p.z+fuzzB, 0))
                elif isCollisionAlert == 101:
                    await drone.offboard.set_position_ned(PositionNedYaw(pos.x-cd,  p.y+fuzzA, p.z+fuzzB, 0))
                elif isCollisionAlert == 102:
                    await drone.offboard.set_position_ned(PositionNedYaw(p.x+fuzzA, pos.y+cd, p.z+fuzzB, 0))
                elif isCollisionAlert == 103:
                    await drone.offboard.set_position_ned(PositionNedYaw(p.x+fuzzA, pos.y-cd, p.z+fuzzB, 0))
                elif isCollisionAlert == 104:
                    await drone.offboard.set_position_ned(PositionNedYaw(p.x+fuzzA, p.y+fuzzB, pos.z+cd, 0))
                elif isCollisionAlert == 105:
                    await drone.offboard.set_position_ned(PositionNedYaw(p.x+fuzzA, p.y+fuzzB, pos.z-cd, 0))
                print(isCollisionAlert)
                await asyncio.sleep(0.2)
            else:
                if wasAlert:
                    await drone.offboard.set_position_ned(PositionNedYaw(p.x, p.y, p.z, 0))

            await asyncio.sleep(0.1)

    print("Goal reached!")
    await asyncio.sleep(5)
    print("Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")


def loadMap(fileName: str, root: Octree):
    def mine(line: str, root: Octree):
        data = line.split(' ')
        pos = Pos(float(data[0]), float(data[1]), float(data[2]))
        size = Pos(float(data[3]), float(data[4]), float(data[5]))
        root.setValue(pos, size, "Obstacle")

    f = open(fileName, "r")
    while f:
        line = f.readline()
        if line == "": break
        mine(line, root)
    f.close()


if __name__ == "__main__":
    Octree.minSize = 0.25 * 0.25 * 0.25
    root = Octree(Pos(0.0, 0.0, -32.0), Pos(32.0, 32.0, 32.0), "Air")
    loadMap("obstacles/obstacles.map", root)
    start = Pos(0.0, 0.0, 0.0)
    goal = Pos(6.0, 0.2, -2.0)
    draw = Draw(Pos(-8.0, -8.0, 0.0), Pos(8.0, 8.0, -8.0))
    path = Astar(start, goal, root, draw)
    draw.showPath(path)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(path))
