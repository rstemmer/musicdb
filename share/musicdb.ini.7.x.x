[meta]
version=5

[server]
pidfile=/var/lib/musicdb/musicdb.pid
statedir=/var/lib/musicdb/mdbstate
fifofile=/var/lib/musicdb/musicdb.fifo
webuiconfig=/var/lib/musicdb/webui.ini

[websocket]
address=127.0.0.1
port=9000
url=wss://localhost:9000
opentimeout=10
closetimeout=5
apikey=WSAPIKEY

[tls]
cert=/var/lib/musicdb/websocket.cert
key=/var/lib/musicdb/websocket.key

[database]
path=/var/lib/musicdb/music.db

[music]
path=MUSICDIR
ignoreartists=lost+found
ignorealbums=
ignoresongs=.directory / desktop.ini / Desktop.ini / .DS_Store / Thumbs.db / README
owner=USER
group=musicdb

[artwork]
path=/var/lib/musicdb/webui/artwork
scales=50, 150, 500
manifesttemplate=/usr/share/musicdb/manifest.appcache.template
manifest=/var/lib/muiscdb/webui/manifest.appcache

[videoframes]
path=/var/lib/musicdb/webui/videoframes
frames=5
scales=150x83
previewlength=3

[uploads]
allow=True
path=/var/lib/musicdb/uploads

[extern]
configtemplate=/usr/share/musicdb/extconfig.ini
statedir=.mdbstate
configfile=config.ini
songmap=songmap.csv

[tracker]
dbpath=/var/lib/musicdb/tracker.db
cuttime=30

[lycra]
dbpath=/var/lib/musicdb/lycra.db

[Icecast]
port=6666
user=source
password=ICECASTSOURCEPASSWORD
mountname=/stream

[Randy]
nodisabled=True
nohated=True
minsonglen=120
maxsonglen=600
songbllen=50
albumbllen=20
artistbllen=10
videobllen=10
maxblage=24
maxtries=10

[log]
logfile=stdout
; or stdout or stderr or journal
loglevel=WARNING
; DEBUG, INFO, WARNING, ERROR or CRITICAL
debugfile=/var/log/musicdb/debuglog.ansi
; or a path to log level DEBUG
ignore=requests, urllib3, PIL

[debug]
disablestats=0
disabletracker=0
disableai=1
disabletagging=0
disableicecast=0
disablevideos=1

; vim: nospell
