from telescope.nexstar import *
from serial import Serial
from multiprocessing import Process, Queue
from telescope import TelescopeCommands, TelescopeCoordinatesType


class NexStarTelescope(object):
    def __init__(self, serial_port, manager):
        self.state = manager.dict()
        self.command_counter = 0
        self.__queue = Queue()
        self.__process = Process(target=NexStarTelescope.processing, args=(self.__queue, self.state, serial_port))
        self.state['coordinate_mode'] = TelescopeCoordinatesType.TELESCOPE_COORDINATES_RA_DEC
        self.state['error'] = False
        self.state['connected'] = False

    def connect(self):
        if not self.__process.is_alive():
            self.__process.run()
            time.sleep(0.5)
            if not self.state['connected']:
                self.__process.close()
                return 1

            if not self.state['error']:
                return 0
        return 1

    def disconnect(self):
        if self.__process.is_alive():
            self.__process.close()

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
        return self.__process.run()

    @staticmethod
    def processing(queue, state,  serial_port):
        try:
            hand_controller = NexstarHandController(Serial(serial_port))
            hand_controller.echo('0')
        except:
            state['error'] = True
            return
        state['connected'] = True
        while True:
            state['c1'], state['c2'] = hand_controller.getPosition()
            if not queue.empty():
                command = queue.get()
                command_type, command_values = command

                if command_type == TelescopeCommands.TELESCOPE_GOTO_POSITION:
                    c1, c2 = command_values
                    if state['coordinates_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_RA_DEC:
                        hand_controller.gotoPosition(c1, c2, NexstarCoordinateMode.RA_DEC)
                    elif state['coordinates_mode'] == TelescopeCoordinatesType.TELESCOPE_COORDINATES_AZM_ALT:
                        hand_controller.gotoPosition(c1, c2, NexstarCoordinateMode.AZM_ALT)

                elif command_type == TelescopeCommands.TELESCOPE_SLEW:
                    rate, axis = command_values
                    if axis == NexstarDeviceId.ALT_DEC_MOTOR or axis == NexstarDeviceId.AZM_RA_MOTOR:
                        hand_controller.slew_fixed(axis, rate)



