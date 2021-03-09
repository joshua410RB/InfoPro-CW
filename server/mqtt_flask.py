import json
import eventlet
import paho.mqtt.client as mqtt
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
workerObject = None


class Worker(object):
    switch = False
    unit_of_work = 0
    accum1 = 0
    accum2 = 0

    def __init__(self, socket_io):
        self.socketio = socket_io
        self.switch = True

    def do_work(self):
        print("Doing work")
        def on_message(client, userdata, message):
            test = message.payload.decode('utf-8').split(":")
            if test[0] == "Device1":
                self.accum1 += int(test[1])
            else:
                self.accum2 += int(test[1])
            dict_data = {"device1": str(self.accum1), "device2": str(self.accum2)}
            print(dict_data)
            dict_data['timestamp'] = str(int(time.time()))
            self.unit_of_work += 1
            self.socketio.emit("update", dict_data, namespace="/work")
            eventlet.sleep(0.01)
        broker_address = 'localhost'
        mqtt_client = mqtt.Client('paho_client_{}'.format(str(int(time.time()))))  # create new instance
        mqtt_client.on_message = on_message  # attach function to callback
        mqtt_client.connect(broker_address, 1883, 60)
        mqtt_client.subscribe('info/accel')
        mqtt_client.loop_forever()

    def stop(self):
        self.switch = False


@app.route("/")
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/work')
def connect():
    print("Connect")
    global worker
    worker = Worker(socketio)
    socketio.emit("re_connect", {"msg": "connected"})


@socketio.on('start', namespace='/work')
def start_work():
    socketio.emit("update", {"msg": "starting worker"})
    socketio.start_background_task(target=worker.do_work)


@socketio.on('stop', namespace='/work')
def stop_work():
    worker.stop()
    socketio.emit("update", {"msg": "worker has been stopped"})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)