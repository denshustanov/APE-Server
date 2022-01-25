import flask
from flask import Flask, jsonify, request, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from camera.gphoto_camera import GPhotoCamera
from telescope.nexstar_telescope import NexStarTelescope
from multiprocessing import Manager
from image import ImageType, ImageManager

manager = Manager()


app = Flask(__name__)

auth = HTTPBasicAuth()

users = {
    'admin': generate_password_hash('admin')
}

cam = GPhotoCamera()

telescope = None

image_manager = ImageManager()


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/images/get-state')
@auth.login_required
def get_images_state():
    global image_manager
    return jsonify(image_manager.get_sessions_json())


@app.route('/images/new-session')
@auth.login_required
def new_session():
    global image_manager
    session_name = request.args.get('name')
    image_manager.new_session(session_name)
    return flask.Response(status=200)


@app.route('/camera/connect')
@auth.login_required
def connect():
    global cam
    status = cam.connect()
    if status == 0:
        return jsonify(cam.get_config_json())
    else:
        return flask.Response(status=500)


@app.route('/images/get-image')
def getImage():
    path = request.args.get('path')
    return send_file(path)


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
    global cam, image_manager
    if cam.connected:
        image_type_str = request.args.get('type')
        image_type = ImageType[image_type_str]
        path = cam.capture_image()
        return image_manager.add_image(path, image_type)
    return flask.Response(status=500)


@app.route('/telescope/scan')
@auth.login_required
def telescope_scan():
    result = NexStarTelescope.scan(manager)
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
