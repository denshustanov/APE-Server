import os

import flask
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import gphoto2 as gp
import rawpy
import imageio

from telescope import nexstar
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

camera_connected = False
camera_config = None
iso_config = None
shutter_speed_config = None
image_format_config = None
images_directory = '/home/deniel/gphoto/flutter/'

telescope = None
telescope_connected = False

telescope_names = [
    '',
    'Celestron GPS Series',
    '',
    'Celestron I Series',
    'Celestron I Series SE',
    'Celestron CGE',
    'Celestron Advanced GT',
    'Celesron SLT',
    '',
    'Celestron CPC',
    'Celestron GT',
    'Celestron SE45',
    'Celestrin SE68'
    '', '', '',
    'Celestron LCM'
]


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/camera/connect')
@auth.login_required
def connect():
    global camera_connected, camera_config, camera, image_format_config, iso_config, shutter_speed_config
    try:
        camera = gp.Camera()
        camera.init()
        camera_connected = True
        camera_config = camera.get_config()

        camera_config_json = {}
        for child in camera_config.get_children():
            for child1 in child.get_children():
                # if str(child1.get_name) in ['imageformat', 'iso', 'shutterspeed']:
                choises = []
                if child1.get_type() == gp.GP_WIDGET_RADIO:
                    for choise in child1.get_choices():
                        if choise:
                            choises.append(str(choise))
                if str(child1.get_name()) == 'cameramodel':
                    camera_config_json["model"] = str(child1.get_value())
                elif str(child1.get_name()) == 'imageformat':
                    image_format_config = child1
                    camera_config_json["image_format"] = {
                        "value": str(child1.get_value()),
                        "choices": choises
                    }
                elif str(child1.get_name()) == 'iso':
                    iso_config = child1
                    camera_config_json["iso"] = {
                        "value": str(child1.get_value()),
                        "choices": choises
                    }
                elif str(child1.get_name()) == 'shutterspeed':
                    shutter_speed_config = child1
                    camera_config_json["shutter_speed"] = {
                        "value": str(child1.get_value()),
                        "choices": choises
                    }
                elif str(child1.get_name()) == 'batterylevel':
                    if str(child1.get_value()) == 'Low':
                        camera_config_json["battery_level"] = 25
                    elif str(child1.get_value()) == '50%':
                        camera_config_json["battery_level"] = 50
                    elif str(child1.get_value()) == '100%':
                        camera_config_json["battery_level"] = 100
        return jsonify(camera_config_json)
    except Exception as e:
        camera_connected = False
        return flask.Response(status=500)


@app.route('/camera/disconnect')
@auth.login_required
def disconnect():
    global camera_connected
    camera.exit()
    camera_connected = False
    return 'Disconnected from camera.'


@app.route('/camera/set-config')
@auth.login_required
def set_config():
    global camera_connected, camera_config, camera
    if camera_connected:
        setting = request.args.get('setting')
        value = request.args.get('value')
        if setting == 'iso':
            iso_config.set_value(value)
        elif setting == 'shutterspeed':
            shutter_speed_config.set_value(value)
        elif setting == 'imageformat':
            image_format_config.set_value(value)
        camera.set_config(camera_config)
        return flask.Response(status=200)
    else:
        return flask.Response(status=500)


@app.route('/camera/capture')
@auth.login_required
def capture():
    if camera_connected:
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
        target = os.path.join(images_directory, file_path.name)
        image_name, image_format = file_path.name.split('.')
        camera_file = camera.file_get(
            file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(target)

        if image_format == 'cr2':
            with rawpy.imread(target) as raw:
                rgb = raw.postprocess()
                imageio.imwrite(images_directory + 'preview/' + image_name + '.jpg', rgb)
            return str(images_directory + 'preview/' + image_name + '.jpg')
        else:
            return target
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
    global telescope, telescope_connected
    port = request.args.get('port')
    telescope = NexStarTelescope(port, manager)
    status = telescope.connect()
    if status == 0:
        return flask.Response(status=200)
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
    if isinstance(telescope, NexStarTelescope):
        if telescope.connected():
            return jsonify(telescope.get_position())
    return flask.Response(status=500)


@app.route('/telescope/goto')
@auth.login_required
def telescope_goto():
    global telescope
    c1 = float(request.args.get('c1'))
    c2 = float(request.args.get('c2'))
    if isinstance(telescope, NexStarTelescope):
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
    if isinstance(telescope, NexStarTelescope) and telescope.connected():
        if motor == 0:
            telescope.slew(nexstar.NexstarDeviceId.ALT_DEC_MOTOR, rate)
        elif motor == 1:
            telescope.slew(nexstar.NexstarDeviceId.AZM_RA_MOTOR, rate)
        return flask.Response(status=200)
    return flask.Response(status=500)


if __name__ == '__main__':
    app.run()
