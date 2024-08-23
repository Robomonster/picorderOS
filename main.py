#!/usr/bin/python

# PicorderOS --------------------------------------------- 2023
# Created by Chris Barrett ------------------------- directive0
# For my sister, a real life Beverly Crusher.

print("PicorderOS")
print("Loading Components")

import os
import sys
from threading import Thread

os.environ['SDL_AUDIODRIVER'] = 'alsa'

from objects import configure, Timer, Events, translate
from sensors import Fragment, Sensor, MLX90614, sensor_process, wifitimer, threaded_sensor
from plars import get_recent_proc, update_proc, update_em_proc, join_dataframes, PLARS, plars_process, plars_obj
from input import Inputs, threaded_input, input_tester
import time


if configure.audio[0]:
    import audio

# This part loads the appropriate modules depending on which preference flags are set.

# load up the LED indicator module
if configure.leds[0]:
    import leds


# The following are only loaded in TR-108 mode
if configure.tr108:
    # Load the TR-108 display modules
    import tos_display


# for the TR-109 there are two display modes supported.
if configure.tr109:

    # 1.8" TFT colour LCD
    if configure.display == 1 or configure.display == 2:
        import lcars_clr

    # Nokia 5110 black and white dot matrix screen.
    if configure.display == 0:
        import lcars_bw

if configure.CLI:
    import cli_display



# the following function is our main loop, it contains all the flow for our program.
def Main():

    # Instantiate a screen object to draw data to screen. Right now for testing
    # they all have different names but each display object should use the same
    # named methods for simplicity sake.
    if configure.tr108:
        screen_object = tos_display.Screen()
        configure.graph_size[0] = screen_object.get_size()

    if configure.tr109:
        if configure.display == 0:
            screen_object = lcars_bw.NokiaScreen()
        if configure.display == 1 or configure.display == 2:
            screen_object = lcars_clr.ColourScreen()
            screen_object.start_up()

        configure.graph_size[0] = screen_object.get_size()

    if configure.CLI:
        screen_object = cli_display.CLI_Display()


    start_time = time.time()


    # The following code sets up the various threads that the rest of the program will use

    # start the sensor loop
    sensor_thread = Thread(target = threaded_sensor, args = ())
    sensor_thread.start()


    # if leds enabled start the event monitor for LEDs
    if configure.leds[0]:
        led_thread = Thread(target = leds.ripple_async, args = ())
        led_thread.start()


    # start the input monitor thread
    input_thread = Thread(target = threaded_input, args = ())
    input_thread.start()

    # start the audio service thread
    if configure.audio[0]:
        audio_thread = Thread(target = threaded_tng_audio, args = ())
        audio_thread.start()

    print("Main Loop Starting")

    # Main loop. Break when status is "quit".
    while configure.status[0] != "quit":

        # try allows us to capture a keyboard interrupt and assign behaviours.
        try:

            screen_object.run()

            if configure.status[0] == "shutdown":
                print("Shut Down!")
                configure.status[0] = "quit"

                if configure.leds[0]:
                    leds.resetleds()

                if configure.input_gpio:
                    leds.cleangpio()

                os.system("sudo shutdown -h now")
                

        # If CTRL-C is received the program gracefully turns off the LEDs and resets the GPIO.
        except KeyboardInterrupt:
            configure.status[0] = "quit"

    print("Quit Encountered")
    print("Main Loop Shutting Down")

    # The following calls are for cleanup and just turn "off" any elements.
    if configure.leds[0]:
        leds.resetleds()
        led_thread.join()

    if configure.input_gpio:
        leds.cleangpio()

    if configure.CLI:
        cli_display.cli_reset()

    if configure.audio[0]:
        audio_thread.join()

    sensor_thread.join()
    input_thread.join()
    plars_obj.shutdown()
    sys.exit()