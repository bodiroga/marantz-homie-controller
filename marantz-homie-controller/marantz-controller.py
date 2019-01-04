#!/usr/bin/env python

import time
import homie
import logging
from MarantzSerialHandler import MarantzSerialHandler

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SERIAL_PORT = "/dev/ttyUSB0"
COMMAND_DELAY = 0.25

config = homie.loadConfigFile("marantz-controller.json")
device = homie.Device(config)

powerNode = device.addNode("power", "power", "power")
volumeNode = device.addNode("volume", "volume", "volume")
speakersNode = device.addNode("speakers", "speakers", "speakers")
sourceNode = device.addNode("source", "source", "source")

powerProperty = powerNode.addProperty("on", "On", datatype="boolean")
volumeProperty = volumeNode.addProperty("volume", "Volume", datatype="integer", format="0:100")
speakersProperty = speakersNode.addProperty("speakers", "Speaker Config", datatype="enum", format="a,b,ab,off")
sourceProperty =  sourceNode.addProperty("source", "Source", datatype="enum", format="tv,dvd,vcr,cd")

class MarantzVolumeMapper(object):

    def __init__(self, original_min=-50, original_max=0, map_min=0, map_max=100):
        self.original_min = original_min
        self.original_max = original_max
        self.map_min = map_min
        self.map_max = map_max

    def original_to_map(self, original):
        original = int(original)
        if original < self.original_min:
            return self.map_min
        elif original > self.original_max:
            return self.map_max
        map = (original-self.original_min)/(self.original_max-self.original_min)*(self.map_max-self.map_min)+self.map_min
        return int(map)

    def map_to_original(self, map):
        map = int(map)
        if map < self.map_min:
            return self.original_min
        elif map > self.map_max:
            return self.original_max
        original = (map-self.map_min)/(self.map_max-self.map_min)*(self.original_max-self.original_min)+self.original_min
        return int(original)

def powerOnHandler(property, value):
    logger.debug("New value '{}' for property '{}'".format(property, value))
    if value == 'true':
        marantz_handler.send_command("@PWR:2")
    else:
        marantz_handler.send_command("@PWR:1")


def volumeValueHandler(property, value):
    logger.debug("New value '{}' for property '{}'".format(property, value))
    if value == 'up':
        marantz_handler.send_command("@VOL:1")
    elif value == 'down':
        marantz_handler.send_command("@VOL:2")
    else:
        original_value = volume_mapper.map_to_original(value)
        marantz_handler.send_command("@VOL:0-{}".format(abs(original_value)))

def sourceValueHandler(property, value):
    logger.debug("New value '{}' for property '{}'".format(property, value))
    if value == 'tv':
        marantz_handler.send_command("@SRC:1")
    elif value == 'dvd':
        marantz_handler.send_command("@SRC:2")
    elif value == 'vcr':
        marantz_handler.send_command("@SRC:3")
    elif value == 'cd':
        marantz_handler.send_command("@SRC:C")


def speakersConfigHandler(property, value):
    logger.debug("New value '{}' for property '{}'".format(property, value))
    if value not in ["a", "b", "ab", "off"]: return
    if value == "a":
        marantz_handler.send_commands(["@SPK:12", "@SPK:21"])
    elif value == "b":
        marantz_handler.send_commands(["@SPK:11", "@SPK:22"])
    elif value == "ab":
        marantz_handler.send_commands(["@SPK:12", "@SPK:22"])
    elif value == "off":
        marantz_handler.send_commands(["@SPK:11", "@SPK:21"])


def event_callback(category, value):
    if category == "PWR":
        powerProperty.update("true" if value=="2" else "false")
    elif category == "VOL":
        volumeProperty.update(volume_mapper.original_to_map(value))
    elif category == "SPK":
        config = ""
        config += "a" if value[0]=="2" else ""
        config += "b" if value[1]=="2" else ""
        if not config: config = "off"
        speakersProperty.update(config)
    elif category == "SRC":
        sources = {"11": "tv", "22": "dvd", "33": "vcr", "3C": "cd"}
        if value in sources:
            sourceProperty.update(sources[value])


def main():
    device.setFirmware("marantz-homie", "1.0.0")

    powerProperty.settable(powerOnHandler)
    volumeProperty.settable(volumeValueHandler)
    speakersProperty.settable(speakersConfigHandler)
    sourceProperty.settable(sourceValueHandler)

    device.setup()

    while True:
        marantz_handler.process()


if __name__ == '__main__':
    try:
        volume_mapper = MarantzVolumeMapper()
        marantz_handler = MarantzSerialHandler(serial_port=SERIAL_PORT, command_delay=COMMAND_DELAY)
        marantz_handler.register_event_callback(event_callback)
        marantz_handler.initialize()
        marantz_handler.initialization_commands()
        main()
    except (KeyboardInterrupt, SystemExit):
        marantz_handler.close()
        logger.info("Quitting.")

