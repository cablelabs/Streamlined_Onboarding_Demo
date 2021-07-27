#from app import app
#from flask_socketio import SocketIO

#socketio = SocketIO(app)
#socketio.run(app,host='0.0.0.0')

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def sessions(methods=['GET','POST']):
    return render_template('index.html')



@app.route('/include/<path:path>')
def send_js(path):
    print("path:{}".format(path))
    return send_from_directory('include', path)


@socketio.on('device_add')
def handle_event(json, methods=['GET', 'POST']):
    print('received device add event: ' + str(json))
    socketio.emit('device_add', json)

@socketio.on('device_remove')
def handle_event(json, methods=['GET', 'POST']):
    print('received device remove event: ' + str(json))
    socketio.emit('device_remove', json)


@socketio.on('device_update')
def handle_event(json, methods=['GET', 'POST']):
    print('received device update event: ' + str(json))
    socketio.emit('device_update', json)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',debug=True)
