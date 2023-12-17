# haxball-server
A drop-in replacement for the HaxBall p2p.haxball.com and p2p2.haxball.com server. It also works for WebLiero, since the two games are basically the same thing when it comes to the networking side.
To install the server, you need:
* Python 3.11
* the Sanic framework
* the `geoip2` module and the GeoLite2-City.mmdb file
* the `tomli` module

To start the server, just type `python server.py` in the terminal.
The server will be running at port 8000.
To enable access to the server in nginx, you can put this in your nginx.conf:
```
location / {
  root   html;
  index  index.html;
}
location /api/ {
  proxy_pass http://127.0.0.1:8000;
}
location /ws/ {
  proxy_pass http://127.0.0.1:8000;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "Upgrade";
  proxy_set_header Host $host;
}
```
Then, run nginx and unzip the included "gamefiles.zip" into the `html` directory.
To run HaxBall, open `http://localhost/play.html` (or `http://localhost/replay.html` for the replays).
To run WebLiero, open `http://localhost/wl/`.
When the games are updated, I'll try to keep up and upload a new `gamefiles.zip`.

For the technical people here (who may want to create their own `gamefiles.zip`):
* the `api/host` POST is removed, because reCaptcha is disabled and `game.min.js` is updated to automatically use a pre-provided response from `api/host`
* this response is `{"url":"ws://" + window.location.host + "/ws/host"}`
* `https://www.haxball.com/rs/` is replaced with `/`
* `wss://p2p.haxball.com/"` is replaced with `"ws://" + window.location.host + "/ws/`

## WARNING
No copyright infringement intended
All game files were made by Mario Carbajal (aka basro) and modified by me
BTW, great job, these games *are* really nice to play
