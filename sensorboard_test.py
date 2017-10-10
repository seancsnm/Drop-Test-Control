"""
Hardware testing of MinimalModbus using Arduino Uno as slave device.

For use with Delta DTB4824VR. 

Usage
-------------

::

    python scriptname [-rtu] [-ascii] [-b38400] [-D/dev/ttyUSB0]

Arguments:
 * -b : baud rate
 * -D : port name
 
NOTE: There should be no space between the option switch and its argument.

Defaults to RTU mode.
"""

import os
import sys
import time

import minimalmodbus

SECONDS_TO_MILLISECONDS = 1000

##############
## Settings ##
##############

DEFAULT_PORT_NAME   = 'COM8'
SLAVE_ADDRESS       = 0x03
DEFAULT_BAUDRATE    = 9600 # baud (pretty much bits/s). Use 2400 or 38400 bits/s.
TIMEOUT             = 1 # seconds. At least 0.2 seconds required for 2400 bits/s.

#########################
## Register Addressses ##
#########################
SENSORS             = 0x00
TIMEA               = 0x01
TIMEB               = 0x02
STATUS              = 0x03
CTRL                = 0x04


#def main():
#################################
## Read command line arguments ##
#################################

# Do manual parsing of command line,
# as none of the modules in the standard library handles python 2.6 to 3.x

MODE        = minimalmodbus.MODE_RTU
BAUDRATE    = DEFAULT_BAUDRATE
PORT_NAME   = DEFAULT_PORT_NAME

for arg in sys.argv:
    if arg.startswith('-ascii'):
        MODE = minimalmodbus.MODE_ASCII
        
    elif arg.startswith('-rtu'): 
        MODE = minimalmodbus.MODE_RTU
    
    elif arg.startswith('-b'):
        if len(arg) < 3:
            minimalmodbus._print_out('Wrong usage of the -b option. Use -b9600')
            sys.exit()
        BAUDRATE = int(arg[2:])
        
    elif arg.startswith('-D'):
        if len(arg) < 3:
            minimalmodbus._print_out('Wrong usage of the -D option. Use -D/dev/ttyUSB0 or -DCOM4')
            sys.exit()
        PORT_NAME = arg[2:]

################################
## Create instrument instance ##
################################
instrument = minimalmodbus.Instrument(PORT_NAME, SLAVE_ADDRESS, MODE)
instrument.serial.baudrate = BAUDRATE
instrument.serial.timeout = TIMEOUT
instrument.debug = False
instrument.precalculate_read_size = True


text = '\n'
text += '###############################################################\n'
text += '## Hardware test with Arduino Uno                          ##\n'
text += '## Minimalmodbus version: {:8}                           ##\n'.format(minimalmodbus.__version__)
text += '##                                                           ##\n'
text += '## Modbus mode:    {:15}                           ##\n'.format(instrument.mode)
text += '## Python version: {}.{}.{}                                     ##\n'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
text += '## Baudrate (-b):  {:>5} bits/s                              ##\n'.format(instrument.serial.baudrate)
text += '## Platform:       {:15}                           ##\n'.format(sys.platform)
text += '##                                                           ##\n'
text += '## Port name (-D): {:15}                           ##\n'.format(instrument.serial.port)
text += '## Slave address:  {:<15}                           ##\n'.format(instrument.address)
text += '## Timeout:        {:0.3f} s                                   ##\n'.format(instrument.serial.timeout)
text += '## Full file path: ' + os.path.abspath(__file__) + '\n'
text += '###############################################################\n'
minimalmodbus._print_out(text)

minimalmodbus._print_out(repr(instrument))

##Read/Write Tests
minimalmodbus._print_out('\SENSORS_0x00: '                        + bin(instrument.read_register(0x0000)))
minimalmodbus._print_out('\TIMEA_0x01: '                          + bin(instrument.read_register(0x0001)))
minimalmodbus._print_out('\TIMEB_0x02: '                          + bin(instrument.read_register(0x0002)))
minimalmodbus._print_out('\STATUS_0x03: '                         + bin(instrument.read_register(0x0003)))
minimalmodbus._print_out('\CTRL_0x04: '                           + bin(instrument.read_register(0x0004)))

#write control register to reset timer
#instrument.write_register(0x0004,0b00000001, 0, functioncode=6)

minimalmodbus._print_out('\SENSORS_0x00: '                        + str(instrument.read_register(0x0000)))
minimalmodbus._print_out('\TIMEA_0x01: '                          + str(instrument.read_register(0x0001)))
minimalmodbus._print_out('\TIMEB_0x02: '                          + str(instrument.read_register(0x0002)))
minimalmodbus._print_out('\STATUS_0x03: '                         + str(instrument.read_register(0x0003)))
minimalmodbus._print_out('\CTRL_0x04: '                           + str(instrument.read_register(0x0004)))
#minimalmodbus._print_out('writing test values')
#instrument.write_register(0x0000,512, 0, functioncode=6)
#time.sleep(0.01) #required time to allow arduino to finish writing register
#minimalmodbus._print_out('\addr0x00: '                        + str(instrument.read_register(0x0000)))
		
#if __name__ == '__main__':
#    main()