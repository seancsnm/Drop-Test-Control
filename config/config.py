##TODO:
# Implement time delay using CMD_DELAY
# Implement COM_TRIES number to communication attempts
# Implement search for mast COM device

import minimalmodbus

##############
## Settings ##
##############

COM_DEVICES         = ['USB-SERIAL'] #List of communication device tags for auto search for master COM device
MODBUS_BAUDRATE            = 115200  #Baud rate to slave devices
MODBUS_MODE                = minimalmodbus.MODE_RTU #Communication mode
MODBUS_TIMEOUT             = 0.05  #Time to wait for response from slave device
#MODBUS_TIMEOUT             = 0.1
CMD_DELAY           = 0.01  #Delay between response from slave device and next command (not yet implemented)
COM_TRIES           = 128     #Number of times master will try to communicate with slave device before 'failing'
DEBUG               = False #If true, debug print statements & functionality enabled
MODBUS_MAX_REFRESH_PERIOD     = 0.150 #Maximum time that may elapse before a locally stored register must be refreshed before accessing

##################################
## Module & Register Addressses ##
##################################

## D1: AUX BOARD
import config_auxboard as D1 #AUX BOARD
import config_mtrctrlboard as D2 # MOTOR CONTROL BOARD
import config_sensorboard as D3 #SENSOR BOARD
