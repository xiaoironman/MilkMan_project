# Introduction

This project is developed for Laterie Lampron, sepcially designed for the recycle box application. The whole program is to be run on a Raspberry pi. The main features include:

  - Touch screen User Interface
  - Electro-magnetic lock control
  - Epson printer control

It can also:
  - Automatically detect system and find the printer port name

# Materials needed
The design is meant to run with the folowing hardware parts:

 - Raspberry Pi
 - Relay switch
 - Electro-magnetic lock
 - LCD screen (Raspberry Pi compatible)
 - Connectors with pinheads
 - Printer

# Dependancies

This project uses a number of open source projects to work properly:

* [kivy] - Open source cross-platform Python library for UI design!
* [Escpos] - Epson printer control python library


# Installation

## Set up the environment
Install Raspbian (with [NOOBS] for example) on your Raspberry Pi and open the command window, create a folder and enter the following command to clone the code:
```sh
$ git clone https://github.com/xiaoironman/MilkMan_project.git
```
Now you should be able to see the project containing all the code and the pictures in the folder.
## Install depandencies for the Epson printer
Install the dependencies with the [official guide for Raspberry Pi]
In brief, what you should do is run the following commands:
```sh
$ sudo apt-get install python3 python3-setuptools python3-pip libjpeg8-dev
$ sudo pip3 install --upgrade pip
$ sudo pip3 install python-escpos
```
Now the printer should be ready to go,.

## Install Kivy
### For Raspberry Pi
PLease refer to the [official installation guide for Raspberry Pi]
### For Windows
In the Windows command window run the following commands:
```sh
$ python -m pip install --upgrade pip wheel setuptools virtualenv
$ python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.22 kivy_deps.glew==0.1.12
$ python -m pip install kivy_deps.gstreamer==0.1.17
$ python -m pip install kivy==1.11.1
```
More details can be found on the kivy [official installation guide for Windows]

# Run
in the raspberry pi command window, go to the path of the project folder and run the following command:
```sh
$ python3 touch_screen.py 
```

# Todos

 - Weighting algorithms
 - Door open detector


   [kivy]: <https://kivy.org/#home>
   [Escpos]: <https://python-escpos.readthedocs.io/en/latest/user/raspi.html>
   [NOOBS]: <https://www.raspberrypi.org/documentation/installation/noobs.md>
   [official guide for Raspberry Pi]: <https://python-escpos.readthedocs.io/en/latest/user/raspi.html>
   [official installation guide for Raspberry Pi]: <https://kivy.org/doc/stable/installation/installation-rpi.html>
   [official installation guide for Windows]: <https://kivy.org/doc/stable/installation/installation-windows.html>
   
