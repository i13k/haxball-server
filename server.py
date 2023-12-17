from sanic import Sanic, json
from sanic.exceptions import BadRequest, NotFound, MethodNotAllowed, SanicException
from sanic.response import text, raw
from asyncio.exceptions import CancelledError

import geoip2.database
import struct
import random
import tomli

app = Sanic("HBServer")

rooms = {}
room_list = b"\x00"

def makeid():
    new_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-", k = ID_LENGTH))
    while new_id in rooms:
        new_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-", k = ID_LENGTH))
    return new_id

def update_room_list():
    global room_list
    room_list = b"\x00"

    for room_id in rooms:
        room = rooms[room_id]

        room_list += struct.pack(">H", len(room_id))
        room_list += room_id.encode("utf-8")
        room_list += struct.pack(">H", len(room["data"]))
        room_list += room["data"]

@app.get("/api/") # welcome message
async def index(request):
    return text("HaxBall v9 server")

@app.get("/api/test") # server health check
async def ping(request):
    return text("OK")

@app.get("/api/notice") # get MOTD (Message Of The Day)
async def notice(request):
    with open("notice.txt") as f:
        content = f.read()
    return json({"data": {"content": content}})

@app.get("/api/geo") # user geolocation API
async def geo(request):
    with geoip2.database.Reader("GeoLite2-City.mmdb") as reader:
        try:
            user_geo = reader.city(request.ip)
        except geoip2.errors.AddressNotFoundError:
            user_geo = reader.city("109.173.231.18")
    return json({"data": {"code": user_geo.country.iso_code, "lat": user_geo.location.latitude, "lon": user_geo.location.longitude}})

@app.get("/api/list") # room list API
async def room_list_get(request):
    return raw(room_list)

@app.websocket("/ws/client") # websocket client-to-host connection tunnel
async def ws_client(request, ws):
    correct = True
    room_id = request.query_string.split("&")[0].split("=") # get the room id from query string

    if len(room_id) < 2: # handle invalid data
        await ws.close(4001)
        correct = False

    room_id = room_id[1]
    if not room_id in rooms:
        await ws.close(4001)
        correct = False

    while correct:
        msg = await ws.recv()
        if msg.startswith(b"\x01"): # make sure we don't parse the dummy \x00 message sent by the client after this one
            rooms[room_id]["clients"].append(ws) # new client connection
            await rooms[room_id]["host"].send(b"\x01" + struct.pack("I", len(rooms[room_id]["clients"]) - 1) + struct.pack("B", len(request.ip)) + request.ip.encode("utf-8") + msg[1:])
            # includes the client ip in the message sent to the host (for ban-checking purposes)

@app.websocket("/ws/host") # host websocket (for gathering information about new clients and broadcasting to room list)
async def ws_host(request, ws):
    room_id = makeid()
    rooms[room_id] = {"host": ws, "clients": []}
    await ws.send(b"\x05" + struct.pack("B", len(room_id)) + room_id.encode("utf-8") + b"\x27thr1.AAAAAGV-zqIrB3ZxMgZM2Q.Abv5uh9vAUw")
    await ws.send(b"\x06thr1.AAAAAGV-zqIrB3ZxMgZM2Q.Abv5uh9vAUw") # token length = 39. this is a dummy token.
    while True:
        try:
            msg = await ws.recv()

            if msg == b"\x08": # ping
                await ws.send(msg) # pong
            
            elif msg.startswith(b"\x07"): # broadcast room data to list
                rooms[room_id]["data"] = msg[1:] # raw room data, sent from the client
                update_room_list()
            
            elif msg.startswith(b"\x01"): # client connection message
                client_id = struct.unpack("I", msg[1:5])[0] # get client id
                await rooms[room_id]["clients"][client_id].send(b"\x01" + msg[5:]) # remove the id from the message and send to client
            
            elif msg.startswith(b"\x00"):
                client_id = struct.unpack("I", msg[1:5])[0] # get client id from message
                
                if len(msg) == 7: # the game host returned an error
                    code = msg[5:] # so we extract the error code
                    rslt = struct.unpack(">H", code)[0] # and convert it to an integer
                    if rslt < 1000 or rslt > 4110: # so that we know the host is being nice
                        rslt = 4100 # when it's not, just reset the code to somthing we know is correct
                    await rooms[room_id]["clients"][client_id].close(rslt) # and then we close the client socket
                
                rooms[room_id]["clients"].pop(client_id) # remove the socket from the list
        except CancelledError: # host disconnected
            del rooms[room_id] # remove the room
            update_room_list()
            break


@app.exception(BadRequest)
async def ignore_400s(request, exception):
    return text("400 bad request", status=400)

@app.exception(NotFound)
async def ignore_404s(request, exception):
    return text("404 page not found", status=404)

@app.exception(MethodNotAllowed)
async def ignore_405s(request, exception):
    return text("405 method not allowed", status=405)

@app.exception(SanicException)
async def ignore_others(request, exception):
    return text("500 server error", status=500)

with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)["server"]

ID_LENGTH = config["id_length"]

if __name__ == "__main__":
    app.run(host=config["host"], port=config["port"], workers=config["workers"])