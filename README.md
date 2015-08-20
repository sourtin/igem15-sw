# Cambridge-JIC 2015 iGEM Team
## Microscopy software
The software is modular and consists of the following layers:
* `hw` -- implements the hardware drivers with python bindings for both the xy translation stage and any heads used
    * `virtual` -- a virtual example and testing XY stage with overhead camera, microscope and pen
    * `shapeoko` -- interface to the shapeoko allowing abstract control and some recovery from disconnection
* `lib` -- provides an interface to the hardware drivers and some nice features:
    * `workspace` -- the `Workspace` class is the primary interface and allows querying the underlying hardware for state and available heads; also provides for enqueuement of head actions and smart (optimised) queueing where a run of head actions can be sorted for reduced time
    * `vector` -- a basic 2d vector library with many useful functions
    * `canvas` -- provides a `Canvas` class which compiles image tiles from the hardware to fill a given polygon and return the resulting image, including automatic updating if image expiration dates are desired; also provides `Polygon` and `Rectangle` classes, as well as the `Image` class for storing image tiles and providing useful helper functions
* `usr` -- a collection of example and user-specified modular experimental routines for actions such as annotation, head & hardware control, and more; can be strung together into an experimental protocol, or even just used for automatic annotation for later browsing, or collecting timelapse images, etc
* `gui` -- the micromaps interface

Note: units to be furlongs, fortnights and firkins

## Installation
* dependencies:
    * `opencv`
    * `openslide` > 3
    * `python` > 3.4
        * `PIL` or `pillow`
        * `pyramid`
        * `opencv-python` > 3
        * `numpy`
        * `openslide` (for tests)

## Contrib
* `marlin` -- fork of `marlin`; arduino firmware for the shapeoko
* `printrun` -- gui interface for controlling `gcode` hardware

## Tests
to run a test, do `./test.py $test`, where `$test` is the name of a test:
* `virtual` -- virtual shapeoko; place `andromeda.tif` ([a gigapixel image of andromeda](https://www.spacetelescope.org/images/heic1502a/), make sure to convert to a pyramidal tif using `vips tiffsave /path/to/original.tif /tmp/andromeda.tif --tile --tile-width=256 --tile-height=256 --pyramid`; you may use the 40K tif rather than the proprietary psb version) in `/tmp`
* `circles` -- home the shapeoko (connected to a `/dev/ttyACM*`) and then move the head in a circle of radius 80 and origin (100,100)
* `serial` -- interact directly with a serial device (e.g. the SO1's marlin firmware via gcode)
* `shapeoko` -- interact with the shapeoko hardware interface, first calibrates the head and moves it a bit
* `needle` -- test shapeoko position consistency by punching some paper with a needle at defined points repeatedly
* `rectangle` -- test shapeoko position consistency by tracing a rectangle repeatedly

alternatively, `./test.py` to list tests

to interact with the shapeoko directly, use `python -m hw.shapeoko.driver` for a wrapped shell or run the `serial` test and connect to the shapeoko's serial port



## Rants
Python 3 is a pita on the raspberry pi because raspbian repos:
1) Only have python 3.2
2) Have less than a fifth of modules available in python2 available as packages for python3
So Souradip refuses to use python 3 because it makes his life so much easier and more time is spent making code instead of head-banging and questioning why package X isn't working.
Also, openslide should really not be a dependancy...

Install nginx first:
    cd /tmp/
    wget http://nginx.org/download/nginx-1.9.4.tar.gz
    cd nginx-1.9.4
    sudo apt-get install build-essential libpcre3-dev
    ./configure --with-http_ssl_module
    make

Or just use the one in pyenv/bin/ I prepared earlier.
Potentially make your own certificates (TODO: document)
Then we can start webshell.

    ./start_webshell.sh should load the python environment and start webshell

TODO:: HTTPS
TODO:: Put mjpg-streamer behind nginx
TODO:: Authentication
TODO:: MicroMaps
