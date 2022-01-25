import datetime
import os
from enum import Enum


class ImageManager(object):
    def __init__(self):
        self.home_directory = 'images/'
        if not os.path.isdir(self.home_directory):
            os.mkdir(self.home_directory)
        self.sessions = []

        for item in os.listdir(self.home_directory):
            path = os.path.join(self.home_directory, item)
            if os.path.isdir(path):
                self.sessions.append(_ImageSession(path, item))
        self.current_session = None

    def new_session(self, session_name):
        self.current_session = _ImageSession(os.path.join(self.home_directory, session_name+'/'), session_name)
        self.sessions.append(self.current_session)

    def add_image(self, image_path, image_type):
        if self.current_session is not None:
            return self.current_session.add_image(image_path, image_type)
        else:
            return image_path

    def get_sessions_json(self):
        result = []

        for session in self.sessions:
            result.append({
                'name': session.name,
                'images': {
                    'lights': session.lights,
                    'darks': session.darks,
                    'flats': session.flats,
                    'biases': session.biases,
                    'tests': session.tests
                }
            })

        return result


class _ImageSession(object):
    def __init__(self, directory, name):
        self.lights_counter = 0
        self.darks_counter = 0
        self.flats_counter = 0
        self.biases_counter = 0
        self.tests_counter = 0

        self.tests = []
        self.lights = []
        self.darks = []
        self.flats = []
        self.biases = []

        self.directory = directory
        self.name = name
        self.lights_directory = os.path.join(directory, 'lights/')
        self.darks_directory = os.path.join(directory, 'darks/')
        self.flats_directory = os.path.join(directory, 'flats/')
        self.biases_directory = os.path.join(directory, 'biases/')
        self.tests_directory = os.path.join(directory, 'tests/')

        if not os.path.isdir(directory):
            os.mkdir(directory)

        if not os.path.isdir(self.darks_directory):
            os.mkdir(self.darks_directory)
        else:
            _ImageSession._scan_images_dir(self.darks_directory, self.darks_counter, self.darks)

        if not os.path.isdir(self.lights_directory):
            os.mkdir(self.lights_directory)
        else:
            _ImageSession._scan_images_dir(self.lights_directory, self.lights_counter, self.lights)

        if not os.path.isdir(self.flats_directory):
            os.mkdir(self.flats_directory)
        else:
            _ImageSession._scan_images_dir(self.flats_directory, self.flats_counter, self.flats)

        if not os.path.isdir(self.biases_directory):
            os.mkdir(self.biases_directory)
        else:
            _ImageSession._scan_images_dir(self.biases_directory, self.biases_counter, self.biases)

        if not os.path.isdir(self.tests_directory):
            os.mkdir(self.tests_directory)
        else:
            _ImageSession._scan_images_dir(self.tests_directory, self.tests_counter, self.tests)



        self.last_image = ''

    def add_image(self, image_path, image_type):
        extension = image_path.split('.')[-1]

        if image_type == ImageType.test:
            self.tests_counter += 1
            new_path = self.tests_directory+'T_'+str(self.tests_counter)+'.'+extension
            self.tests.append(new_path)

        elif image_type == ImageType.light:
            self.lights_counter += 1
            new_path = self.lights_directory + 'L_' + str(self.lights_counter) + '.' + extension
            self.lights.append(new_path)

        elif image_type == ImageType.dark:
            self.darks_counter += 1
            new_path = self.darks_directory + 'D_' + str(self.darks_counter) + '.' + extension
            self.darks.append(new_path)

        elif image_type == ImageType.flat:
            self.flats_counter += 1
            new_path = self.flats_directory + 'F_' + str(self.flats_counter) + '.' + extension
            self.flats.append(new_path)

        elif image_type == ImageType.bias:
            self.biases_counter += 1
            new_path = self.biases_directory + 'B_' + str(self.biases_counter) + '.' + extension
            self.biases.append(new_path)

        with open(image_path, 'rb') as image_file:
            image = image_file.read()

        with open(new_path, 'wb') as new_image_file:
            new_image_file.write(image)

        os.remove(image_path)
        return new_path

    @staticmethod
    def _scan_images_dir(directory, counter, im_list):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                counter += 1
                im_list.append(item_path)


class ImageType(Enum):
    light = 0
    dark = 1
    flat = 2
    bias = 3
    test = 4
