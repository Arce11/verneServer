import trio
import httpx
import random

# NOTA: trio Y httpx SON NECESARIOS PARA ESTE SCRIPT (NO LISTADOS EN requirements.txt)
ROVER_ID = "virtual_verne"
ROVER_ADDRESS = "127.0.0.1"
SESSION_ID = "asassdgfhksda5"
SERVER_ADDRESS = "http://127.0.0.1/"
# SERVER_ADDRESS = "http://ec2-13-53-130-185.eu-north-1.compute.amazonaws.com/"

session_params = {
    "session_id": SESSION_ID,
    "rover_id": ROVER_ID,
    "temperature": 15,
    "pressure": 1013,
    "humidity": 70,
    "num_satellites": 4,
    "latitude": 43.5322,
    "longitude": -5.6611,
    "altitude": 100,
    "battery": 100,
    "rssi": -40,
    "motor_current": 1,
    "message": "Astronauta virtual...",
    "session_state": "VIRTUAL",
    "session_substate": "virtual"
}


def calculate_new_parameter(prev_value, mean, std_deviation, min_value, max_value):
    new_value = max_value + 1
    while new_value > max_value or new_value < min_value:
        new_value = prev_value + random.gauss(mean, std_deviation)
    return new_value


async def timer():
    counter = 0
    while True:
        print(f"### {counter:04}s ###")
        counter = counter + 2
        await trio.sleep(2)


async def launch_virtual_rover():
    async with httpx.AsyncClient() as client:
        # ----------- REGISTER ROVER ---------------------------
        msg = {'rover_id': ROVER_ID, 'address': ROVER_ADDRESS}
        print(f"----> REGISTER ROVER: \t {msg}")
        ans = await client.post(SERVER_ADDRESS + "api/rover/", json=msg)
        print(f"<---- ANSWER STATUS: {ans.status_code}")

        # ----------- REGISTER SESSION --------------------------
        msg = {'session_id': SESSION_ID, 'rover_id': ROVER_ID}
        print(f"----> REGISTER SESSION: \t {msg}")
        ans = await client.post(SERVER_ADDRESS + "api/session/", json=msg)
        print(f"<---- ANSWER STATUS: {ans.status_code}")

        # ----------- UPDATE ROVER --------------------------
        msg = {'rover_id': ROVER_ID, 'last_session': SESSION_ID, 'address': ROVER_ADDRESS}
        print(f"----> UPDATE ROVER: \t {msg}")
        ans = await client.put(SERVER_ADDRESS + "api/rover/" + ROVER_ID + "/", json=msg)
        print(f"<---- ANSWER STATUS: {ans.status_code}")

        # ----------- UPDATE SESSION ------------------------
        while True:
            session_params['temperature'] = calculate_new_parameter(session_params['temperature'], 0, 1, 0, 50)
            print(f"\tUpdated temperature: {session_params['temperature']}")
            session_params['pressure'] = calculate_new_parameter(session_params['pressure'], 0, 4, 700, 1300)
            print(f"\tUpdated pressure: {session_params['pressure']}")
            session_params['humidity'] = calculate_new_parameter(session_params['humidity'], 0, 2, 0, 100)
            print(f"\tUpdated humidity: {session_params['humidity']}")
            session_params['latitude'] = calculate_new_parameter(session_params['latitude'], 0, 0.0005, 43.50, 43.5580)
            print(f"\tUpdated latitude: {session_params['latitude']}")
            session_params['longitude'] = calculate_new_parameter(session_params['longitude'], 0, 0.001, -5.9, -5.6)
            print(f"\tUpdated longitude: {session_params['longitude']}")
            session_params['altitude'] = calculate_new_parameter(session_params['altitude'], 0.1, 0.5, 0, 500)
            print(f"\tUpdated altitude: {session_params['altitude']}")
            if session_params['battery'] < 2:
                session_params['battery'] = 100
            else:
                session_params['battery'] = calculate_new_parameter(session_params['battery'], -0.1, 0.2,
                                                                    session_params['battery']-3,
                                                                    session_params['battery'])
            print(f"\tUpdated battery: {session_params['battery']}")
            session_params['rssi'] = calculate_new_parameter(session_params['rssi'], 0, 1, -70, 10)
            print(f"\tUpdated rssi: {session_params['rssi']}")
            print(f"----> UPDATE SESSION: \t {session_params}")
            try:
                ans = await client.put(SERVER_ADDRESS + "api/session/" + SESSION_ID + "/", json=session_params)
                print(f"<---- ANSWER STATUS: {ans.status_code}")
            except httpx.RemoteProtocolError:
                print("wtf")
            await trio.sleep(1)


async def parent():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(timer)
        nursery.start_soon(launch_virtual_rover)


trio.run(parent)
