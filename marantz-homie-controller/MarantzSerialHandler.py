import time
import serial
import queue
import logging

logger = logging.getLogger(__name__)

class MarantzSerialHandler(object):

    def __init__(self, serial_port, baudrate=9600, timeout=0, command_delay=0):
        self.serial_port = serial_port
        self.command_delay = command_delay
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.buffer = b''
        self.command_queue = queue.Queue(12)
        self.last_command_time = 0
        self.event_callbacks = []

    def initialize(self):
        self.serial_conn = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=self.timeout)

    def __send_command(self, command):
        c = "{}\r\n".format(command)
        self.serial_conn.write(c.encode())
        logger.debug("Command '{}' executed from queue".format(command))
        self.last_command_time = time.time()

    def __analize_message(self, message):
        category=message[:3].decode()
        value=message[4:].decode()
        for callback in self.event_callbacks:
            callback(category, value)

    def initialization_commands(self):
        self.send_command("@AST:F")
        self.send_command("@PWR:?")
        self.send_command("@VOL:?")
        self.send_command("@SPK:?")
        self.send_command("@SRC:?")

    def send_command(self, command):
        self.command_queue.put(command)
        logger.debug("New command '{}' added to the queue".format(command))

    def send_commands(self, commands):
        if not type(commands) is list:
            logger.error("Commands '{}' is not a list".format(commands))
        for command in commands:
            self.send_command(command)

    def process(self):
        char = self.serial_conn.read()
        if char:
            if char == b'@':
                self.buffer = b''
            elif char == b'\r':
                self.__analize_message(self.buffer)
                self.buffer = b''
            else:
                self.buffer += char
        if not self.command_queue.empty():
            if time.time() - self.last_command_time > self.command_delay:
               command = self.command_queue.get_nowait()
               self.__send_command(command)

    def register_event_callback(self, callback):
        if not callback in self.event_callbacks:
            self.event_callbacks.append(callback)

    def close(self):
        self.serial_conn.close()


if __name__ == "__main__":

    def c(category, value):
        print("Category: {}, value: {}".format(category,value))

    controller = MarantzSerialHandler("/dev/ttyUSB0", command_delay=0.25)
    controller.register_event_callback(c)
    controller.initialize()
    controller.initialization_commands()

    while(True):
        controller.process()
