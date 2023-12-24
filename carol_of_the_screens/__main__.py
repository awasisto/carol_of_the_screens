import csv
import json
import sys
import threading
from datetime import datetime, timedelta
from time import sleep

from flask import Flask, render_template, Response
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket

app = Flask(__name__)
sockets = Sockets(app)

websockets = {}

active_threads = 0


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/music')
def music():
    def generate():
        with open(f'{sys.argv[1]}', "rb") as f:
            chunk = f.read(1024)
            while chunk:
                yield chunk
                chunk = f.read(1024)

    return Response(generate(), mimetype='audio/mp3')


@sockets.route('/ws')
def ws(websocket: WebSocket):
    client_number = None
    while not websocket.closed:
        message = json.loads(websocket.receive())
        if message['action'] == 'ready':
            client_number = int(message['client_number'])
            websockets[client_number] = websocket
        elif message['action'] == 'play':
            threading.Thread(target=play).start()


def play():
    start_time = datetime.utcnow() + timedelta(seconds=3)
    last_sleep_time = start_time

    for websocket in websockets.values():
        websocket.send(json.dumps({'action': 'lights_out'}))

    for client_number in websockets.keys():
        threading.Thread(target=schedule_send, args=(client_number, start_time, json.dumps({'action': 'play_music'}))).start()

    with open(sys.argv[2]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            light_relative_time = datetime.strptime(row[0], '%H:%M:%S.%f')
            light_absolute_time = start_time + timedelta(hours=light_relative_time.hour, minutes=light_relative_time.minute, seconds=light_relative_time.second, milliseconds=light_relative_time.microsecond / 1000)
            light_duration_seconds = float(row[1])
            threading.Thread(target=schedule_send, args=(int(row[2]), light_absolute_time, json.dumps({'action': 'light', 'color': row[3], 'duration_seconds': light_duration_seconds}))).start()

            if last_sleep_time + timedelta(seconds=6) < light_absolute_time:
                sleep(3)
            last_sleep_time = datetime.utcnow()



def schedule_send(client_number: int, send_at: datetime, message: str):
    global active_threads
    active_threads += 1
    print(f'{active_threads} active threads\n', end='')
    sleep((send_at - datetime.utcnow()).total_seconds())
    try:
        websockets[client_number].send(message)
    except:
        pass
    active_threads -= 1
    print(f'{active_threads} active threads\n', end='')


server = pywsgi.WSGIServer(('0.0.0.0', 8080), application=app, handler_class=WebSocketHandler)
server.serve_forever()
