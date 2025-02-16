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
