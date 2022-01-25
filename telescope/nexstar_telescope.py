import glob
from telescope.nexstar import *
from serial import Serial
from multiprocessing import Process, Queue
from telescope import TelescopeCommands, TelescopeCoordinatesType


class NexStarTelescope(object):
    def __init__(self, serial_port, manager):
        self.state = manager.dict()
        self.command_counter = 0
        self.__queue = Queue()
        self.__process = Process(target=NexStarTelescope.__processing, args=(self.__queue, self.state, serial_port))
        self.__process.daemon = True
        self.state['coordinate_mode'] = TelescopeCoordinatesType.TELESCOPE_COORDINATES_RA_DEC
        self.state['error'] = False
        self.state['connected'] = False
        self.state['model_name'] = ''

    def connect(self):
        if not self.__process.is_alive():
            self.__process.start()
            print('connecting...')
            time.sleep(2)
            if not self.state['connected']:
                self.__process.close()
                return 1

            if self.state['error']:
                return 1
            print('connected')
            return 0
        return 1

    def disconnect(self):
        self.__queue.put(TelescopeCommands.TELESCOPE_DISCONNECT)

    def set_coordinates_mode(self, mode):
        if mode in TelescopeCoordinatesType:
            self.state['coordinate_mode'] = mode

    def goto(self, c1, c2):
        self.__queue.put((TelescopeCommands.TELESCOPE_GOTO_POSITION, (c1, c2)))

    def slew(self, rate, axis):
        self.__queue.put((TelescopeCommands.TELESCOPE_SLEW, (rate, axis)))

    def get_position(self):
        return self.state['c1'], self.state['c2']

    def connected(self):
        return self.__process.is_alive()

    def get_model_name(self):
        return self.state['model_name']

    @staticmethod
    def __processing(queue, state, serial_port):
        try:
            hand_controller = NexstarHandController(Serial(serial_port))
            hand_controller.echo(0)
            state['model_name'] = NexstarModel(hand_controller.getModel()).name

            state['connected'] = True
            while True:
                if state['coordinate_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_RA_DEC:
                    state['c1'], state['c2'] = hand_controller.getPosition(coordinateMode=NexstarCoordinateMode.RA_DEC)
                if state['coordinate_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_AZM_ALT:
                    state['c1'], state['c2'] = hand_controller.getPosition(coordinateMode=NexstarCoordinateMode.AZM_ALT)
                if not queue.empty():
                    command = queue.get()
                    command_type, command_values = command

                    if command_type == TelescopeCommands.TELESCOPE_GOTO_POSITION:
                        c1, c2 = command_values
                        if state['coordinate_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_RA_DEC:
                            hand_controller.gotoPosition(c1, c2, NexstarCoordinateMode.RA_DEC)
                        elif state['coordinate_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_AZM_ALT:
                            hand_controller.gotoPosition(c1, c2, NexstarCoordinateMode.AZM_ALT)

                    elif command_type == TelescopeCommands.TELESCOPE_SLEW:
                        rate, axis = command_values
                        if axis == 0:
                            print(NexstarDeviceId.ALT_DEC_MOTOR.name, rate)
                            hand_controller.slew_fixed(NexstarDeviceId.ALT_DEC_MOTOR, rate)
                        if axis == 1:
                            print(NexstarDeviceId.AZM_RA_MOTOR.name, rate)
                            hand_controller.slew_fixed(NexstarDeviceId.AZM_RA_MOTOR, rate)

                    elif command_type == TelescopeCommands.TELESCOPE_DISCONNECT:
                        hand_controller.close()
                        break

        except Exception as e:
            print(e)
            state['error'] = True
            return

    @staticmethod
    def scan(manager):
        ports = glob.glob('/dev/tty[A-Za-z]*')
        mounts = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                mount = NexStarTelescope(port, manager)
                mount.connect()
                model_name = mount.get_model_name()
                mounts.append({
                    'model': model_name,
                    'port': port
                })
            except Exception as e:
                print(e)
                pass
