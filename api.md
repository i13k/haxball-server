# HaxBall/WebLiero API documentation
HaxBall API: `https://www.haxball.com/rs/api/`
WebLiero API: `https://api.webliero.com/`
## `/api/list` -- Room List
### Response format:
First byte -- always `00`
Then for each room:
* big-endian uint16 -- room ID length
* room ID (UTF-8)
* big-endian uint16 -- room data length
* room data
### Room data format:
* uint16 -- room version
* uint8 -- room name length
* utf-8 -- room name
* uint8 -- flag code length
* utf-8 -- flag code
* float32 -- latitude
* float32 -- longitude
* uint8 -- password flag [0/1]
* uint8 -- player limit
* uint8 -- players connected
## `/api/geo` -- Geolocalization Api
### Response format:
`{"data":{"code":"CC","lat":0.0000,"lon":0.0000}}`
(where CC -- two-letter country code, [lat, lon] -- latitude and longitude
## `/api/notice` -- Notice
### Response format:
`{"data":{"content":"ABCDE"}}`
(where ABCDE -- notice content, empty string if there's no notice)
## `/api/host` -- Request to get token to host a game
### Request format:
This endpoint only accepts POST requests.
The request body muse be encoded with the standard format (`key1=value1&key2=value2&key3=value3` etc.).

Request body format: `token=TOKEN&rcr=RCR` (where `TOKEN` -- an optional token (if not provided, must be an empty string), and `RCR` -- the response from reCaptcha, may be an empty string).
### Response format:
The response is JSON-encoded.
* `{"data":{"action":"recaptcha","sitekey":"SITEKEY"}}` -- instructs the client to display a reCaptcha dialog using the site key `SITEKEY`.
* `{"data":{"action":"connect","url":"wss://p2p2.webliero.com/host","token":"TOKEN"}}` -- instructs the client to connect to the specified WebSocket URL and append `?token=TOKEN` to the URL.
## `/api/client` -- Request to join a reCaptcha-protected room
### Request format:
The request body muse be encoded with the standard format (`key1=value1&key2=value2&key3=value3` etc.).
Request body format: `room=ROOM_ID&rcr=RCR` (where `ROOM_ID` is the ID of the room the client is trying to connect to, and `RCR` is the reCaptcha response).
### Response format:
The same as with `/api/host`.
