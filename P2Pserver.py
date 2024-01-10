# HaxBall Server v2.2
import asyncio
import websockets
import struct
import redis

from random import choices

r = redis.Redis()

rooms = {}
clients = []

def update_room_list():
    room_list = b"\x00"

    for room_id in rooms:
        room_data = r.get(room_id)

        room_list += struct.pack(">H", len(room_id))
        room_list += room_id.encode("utf-8")
        room_list += struct.pack(">H", len(room_data))
        room_list += room_data
    r.set("room_list", room_list)

async def client(ws, room_id):
    try:
        client_ip = ws.remote_address[0]
        clients.append(ws)
        client_id = len(clients) - 1
        msg = await ws.recv()
        await rooms[room_id].send(b"\x01" + struct.pack("I", client_id) + struct.pack("B", len(client_ip)) + client_ip.encode("utf-8") + msg[1:])
        await ws.recv()
        await ws.recv()
    except (Exception, BaseException):
        clients.pop(client_id)

async def host(ws):
    room_id = "".join(choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-", k=11))
    while room_id in rooms:
        room_id = "".join(choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-", k=11))
    rooms[room_id] = ws
    await ws.send(b"\x05" + struct.pack("B", len(room_id)) + room_id.encode("utf-8") + b"\x27thr1.AAAAAGV-zqIrB3ZxMgZM2Q.Abv5uh9vAUw")
    while True:
        try:
            msg = await ws.recv()
            msg_type = msg[0]

            if msg_type == 0:
                client_id = struct.unpack("I", msg[1:5])[0]
                if len(msg) == 7:
                    code = struct.unpack(">H", msg[5:])[0]
                    if code < 1000 or code > 4110:
                        code = 4100
                    await clients[client_id].close(code)
                clients.pop(client_id)

            elif msg_type == 1:
                client_id = struct.unpack("I", msg[1:5])[0]
                await clients[client_id].send(b"\x01" + msg[5:])

            elif msg_type == 7:
                r.set(room_id, msg[1:])
                update_room_list()

            elif msg_type == 8:
                await ws.send(b"\x08")

        except (Exception, BaseException):
            del rooms[room_id]
            r.delete(room_id)
            update_room_list()
            break

async def handler(ws):
    if ws.path == "/host":
        await host(ws)
    elif ws.path.startswith("/client?id="):
        room_id = ws.path.split("=")[1]
        if room_id not in rooms:
            return
        await client(ws, room_id)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000, server_header=None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
