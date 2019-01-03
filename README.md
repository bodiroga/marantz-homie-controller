# Marantz-Homie Controller

## Introduction

Marantz-Homie Controller is a python3 service to control a Marantz A/V receiver (tested on SR5001 model) using the RS232 port. The service exposes its functionality as a Homie 3 device, so any MQTT client can send remote commands.

## Features

Supported functions:

- Power ON/OFF
- Volume control
- Speakers control (a, b, ab and off)
- Source control (tv, cd, dvd, vcr)

> Warning: homie-python V3 library is required. See: https://github.com/jalmeroth/homie-python/pull/47

## Installation

The script has been succesfully tested on a Raspberry Pi, but it should work on any Debian based (Ubuntu) distribution.

wget https://raw.githubusercontent.com/bodiroga/marantz-homie-controller/master/install.sh && chmod +x install.sh

sudo ./install.sh

Enjoy!