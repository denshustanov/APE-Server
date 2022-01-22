import os

import flask
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import gphoto2 as gp
import rawpy
import imageio

from telescope import nexstar
from camera.gphoto_camera import GPhotoCamera
import glob
import serial
from telescope.nexstar_telescope import NexStarTelescope
from multiprocessing import Manager

manager = Manager()


app = Flask(__name__)

auth = HTTPBasicAuth()

users = {
    'admin': generate_password_hash('admin')
}

cam = GPhotoCamera()

telescope = None


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/camera/connect')
@auth.login_required
def connect():
    global cam
    status = cam.connect()
    if status == 0:
        return jsonify(cam.get_config_json())
    else:
        return flask.Response(status=500)


@app.route('/camera/disconnect')
@auth.login_required
def disconnect():
    global cam
    cam.disconnect()
    return 'Disconnected from camera.'


@app.route('/camera/set-config')
@auth.login_required
def set_config():
    global cam
    if cam.connected:
        setting = request.args.get('setting')
        value = request.args.get('value')
        if setting == 'iso':
            cam.set_iso(value)
        elif setting == 'shutterspeed':
            cam.set_shutter_speed(value)
        elif setting == 'imageformat':
            cam.set_image_format(value)
        return flask.Response(status=200)
    else:
        return flask.Response(status=500)


@app.route('/camera/capture')
@auth.login_required
def capture():
    global cam
    if cam.connected:
        return cam.capture_image()
    return flask.Response(status=500)


@app.route('/telescope/scan')
@auth.login_required
def telescope_scan():
    ports = glob.glob('/dev/tty[A-Za-z]*')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except Exception as e:
            pass
    return jsonify(result)


@app.route('/telescope/connect')
@auth.login_required
def connect_telescope():
    global telescope
    port = request.args.get('port')
    telescope = NexStarTelescope(port, manager)
    status = telescope.connect()
    if status == 0:
        return telescope.get_model_name()
    else:
        return flask.Response(status=500)


@app.route('/telescope/disconnect')
@auth.login_required
def disconnect_telescope():
    global telescope
    if telescope is not None:
        if isinstance(telescope, NexStarTelescope):
            telescope.disconnect()
    return flask.Response(status=200)


@app.route('/telescope/get-position')
@auth.login_required
def telescope_get_position():
    global telescope
    if telescope.connected():
         return jsonify(telescope.get_position())
    return flask.Response(status=500)


@app.route('/telescope/goto')
@auth.login_required
def telescope_goto():
    global telescope
    c1 = float(request.args.get('c1'))
    c2 = float(request.args.get('c2'))
    if telescope.connected():
        telescope.goto(c1, c2)
        return flask.Response(status=200)
    return flask.Response(status=500)


@app.route('/telescope/slew')
@auth.login_required
def telescope_slew():
    global telescope
    motor = int(request.args.get('motor'))
    rate = int(request.args.get('rate'))
    telescope.slew(rate, motor)
    return flask.Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
