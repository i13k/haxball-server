# HaxBall/WebLiero WebSocket protocol
HaxBall server: `p2p.haxball.com`, `p2p2.haxball.com`; WebLiero server: `p2p.webliero.com`
## `/test` -- Healthcheck
Response: always `200 OK` with `content-type: text/plain`; response content: `OK`
## `/client?id=<ROOM_ID>&token=tcr1.X.Y` -- Connect to room
`<ROOM_ID>` -- room ID; `token` -- token to join the room. Only required when reCaptcha is enabled.

The messages are in a binary format, where the first byte indicates the type of the message.
This connection is usually closed once the host replies to the client's message.

If the room is protected by reCaptcha and the token was not provided or incorrect, the server must close the connection with the code `4004`.
### Message Types (Client to Server)
* `01` -- Save message to host -- the rest of the message is what should be sent to the host
* `00` -- Send message to host -- indicated that the previously saved message should be sent
### Message Types (Server to Client)
* `01` -- Receive Message from Host -- the rest of the message is what the host sent
## `/host?token=thr1.X.Y` -- Create new room
The token may be optional. The messages are in a binary format, where the first byte indicates the type of the message.
This connection is open for the entire lifetime of the room.
### Message Types (Client to Server)
* `00` -- Close client connection. Closes the client socket with ID indicated by the next four bytes with the code indicated by the following two bytes (format: big-endian `uint16`). If the close code is not provided, the socket will not be closed, but this still indicates that the host is done with the specified client. In this case, the client should close the connection, not the server.
* `01` -- Send message to client. The ID of the client is specified in the next four bytes, the rest is the message itself.
* `07` -- Broadcast room data. Tells the server that the room data (available from `/api/list`) for this room should be replaced with the rest of the message.
* `08` -- Ping. Used to keep the connection alive. Should be sent by the client.
* `09` -- reCaptcha -- next byte is `00` or `01`, indicating whether reCaptcha verification for this room should be disabled or enabled.
### Message Types (Server to Client)
* `01` -- Receive message from client -- contents:
  1. client ID -- 4 bytes
  2. client IP length -- uint8 -- 1 byte
  3. client IP -- UTF-8
  4. the message sent by the client.
* `05` -- initialize host -- contents:
  1. room ID length -- uint8 -- usually 11 (`0x0B`)
  2. room ID
  3. token length -- uint8 -- usually 39 (`0x27`)
  4. token
* `08` -- pong -- must be sent as a response to the ping message sent by the client.
