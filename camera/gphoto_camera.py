import gphoto2
import os
import rawpy
import imageio


class GPhotoCamera(object):
    def __init__(self):
        self.cam = gphoto2.Camera()
        self.config = None
        self.connected = False

        self.manufacturer = None
        self.model = None
        self.shutter_counter = 0

        self.iso_config = None
        self.shutter_speed_config = None
        self.image_format_config = None

        self.iso_choices = []
        self.shutter_speed_choices = []
        self.image_format_choices = []
        self.battery_level = 0

        self.images_directory = ''

    def connect(self):
        try:
            self.cam.init()
            self.connected = True
            self.config = self.cam.get_config()

            for child in self.config.get_children():
                for child1 in child.get_children():
                    choices = []
                    if child1.get_type() == gphoto2.GP_WIDGET_RADIO:
                        for choise in child1.get_choices():
                            if choise:
                                choices.append(str(choise))
                    if str(child1.get_name()) == 'cameramodel':
                        self.model = str(child1.get_value())

                    elif str(child1.get_name()) == 'imageformat':
                        self.image_format_config = child1
                        self.image_format_choices = choices

                    elif str(child1.get_name()) == 'iso':
                        self.iso_config = child1
                        self.iso_choices = choices

                    elif str(child1.get_name()) == 'shutterspeed':
                        self.shutter_speed_config = child1
                        self.shutter_speed_choices = choices

                    elif str(child1.get_name()) == 'batterylevel':
                        if str(child1.get_value()) == 'Low':
                            self.battery_level = 25
                        elif str(child1.get_value()) == '50%':
                            self.battery_level = 50
                        elif str(child1.get_value()) == '100%':
                            self.battery_level = 100
            return 0
        except:
            return 1

    def disconnect(self):
        self.cam.exit()
        self.connected = False

    def set_iso(self, iso):
        if self.connected:
            if iso in self.iso_choices:
                self.iso_config.set_value(iso)
                self.cam.set_config(self.config)

    def set_shutter_speed(self, shutter_speed):
        if self.connected:
            if shutter_speed in self.shutter_speed_choices:
                print(shutter_speed)
                self.shutter_speed_config.set_value(shutter_speed)
                self.cam.set_config(self.config)

    def set_image_format(self, image_format):
        if self.connected:
            if image_format in self.image_format_choices:
                self.image_format_config.set_value(image_format)
                self.cam.set_config(self.config)

    def capture_image(self):
        file_path = self.cam.capture(gphoto2.GP_CAPTURE_IMAGE)
        target = os.path.join(self.images_directory, file_path.name)
        image_name, image_format = file_path.name.split('.')
        camera_file = self.cam.file_get(
            file_path.folder, file_path.name, gphoto2.GP_FILE_TYPE_NORMAL)
        camera_file.save(target)

        if image_format == 'cr2':
            with rawpy.imread(target) as raw:
                rgb = raw.postprocess()
                imageio.imwrite(self.images_directory + 'preview/' + image_name + '.jpg', rgb)
            return str(self.images_directory + 'preview/' + image_name + '.jpg')
        else:
            return target

    def get_config_json(self):
        config_json = {
            "iso": {
                "value": str(self.iso_config.get_value()),
                "choices": self.iso_choices
            },
            "shutter_speed": {
                "value": str(self.shutter_speed_config.get_value()),
                "choices": self.shutter_speed_choices
            },
            "image_format": {
                "value": str(self.image_format_config.get_value()),
                "choices": self.image_format_choices
            },
            "model": self.model,
            "shutter_counter": self.shutter_counter
        }

        return  config_json


