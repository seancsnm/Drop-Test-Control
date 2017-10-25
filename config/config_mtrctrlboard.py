##D2: MOTOR CONTROL BOARD DEFINITIONS
"""Copied from MtrCtrl_Board1 ino:
/* Runs the motors and solenoid valves on the device. 
 * This board has support for 4 solenoids (2 independent, 3 & 4 controlled by single pin). Solenoid voltage is controlled by a jumper, which can provide either 12 or 24 volts. 
 * The solenoids should open when high and closed when low. 
 * 
 * The module supports 2 motors. It uses the DRV8704 motor controller, which has an adjustable current limit feature. The current and motor drive direction can remotely be 
 * controlled. Motor 1 - the winch motor - is setup so that it will only raise while the TOP_TRIP_SENSOR pin is low. Both motors will only operate when the EN pin is active. 
 * 
 * Register and register bit functions are described in their enumerations/declarations
 * 
 * Example control sequence is as follows:
 *  0) User ensures device is enabled by making sure gate is closed and master device has PI_EN bit set on auxiliary module
 *  1) Master device sets current limit on device for trolley motor
 *  2) User may switch to manual control mode to raise/lower the winch using the remote control (current code setup may have safety hazard, as this requires that enable signal
 *  be high to control the motors manually or automatically. Fix may be to allow the user to manually control the winch when device is not enabled until the top trip sensor is
 *  tripped, since that will be when trolley docks to the magnet, and when lowering the winch places the trolley's load on the magnet. Will have to think about this more... Maybe 
 *  allow user to continue raising winch once docking sensor is tripped, but not lower it, in order to ensure that it is correctly seated on magnet? 
 *  3) Once trolley is docked, ensure all personnel are clear from area
 *  4) Lower winch to release trolley from winch, then raise to clear hook from trolley
 *  5) Master device may initiate test, which means activating solenoids immediately after releasing electromagnet. The timing may need to occur on the microcontroller side
 *  instead of the master side... Something like 15 ms delay will exist. 
 *  6) De-activate solenoid valves after specified period of time 
 */
 """

ADDR                  = 0x02 #Device slave address

#Register Definitions
STATUS                = 0x00 #Status of the system, viewed by master
POTS                  = 0x01 #bits 0-7 (potentiometer A ADC reading, truncated to 8 bits), bits 8-15 (potentiometer B ADC reading, truncated to 8 bits) - currently for debugging only
CUR_CTRL              = 0x02 #8-bit current control in deca-amps (i.e. a value of 80 = 8.0 amps). Set by master
TORQUE                = 0x03 #Torque value that sets the motor controller internal register. Currently for debugging only
DEV_CTRL              = 0x04 #Contains control bits that are set/cleared by master
TIMER                 = 0x05 #For debugging (times main loop iteration time)
COUNTER               = 0x06 #For debugging (number of main loop iterations elapsed)
DEBUG                 = 0x07 #For debugging (arbitrary)

#STATUS register
EN                    = 0 #Global enable pin - required to enable electromagnets and all modules
TOP_TRIP_SENSOR       = 1 #Docking sensor state
MTR_CTRL_SW           = 2 #Switch state that switches between remote control mode (low) and master control mode (high)
M_A1                  = 3 #Motor controller A-1 pin state
M_A2                  = 4 #Motor controller A-2 pin state
M_B1                  = 5 #Motor controller B-1 pin state
M_B2                  = 6 #Motor controller B-2 pin state
SPI_ERR0              = 7 #SPI error code 1 (failed to set ISENSE register)
SPI_ERR1              = 8 #SPI error code 2 (failed to set TORQUE)
SPI_ERR2              = 9 #SPI error code 3 (reserved)
SPI_ERR3              = 10 #SPI error code 4 (reserved)

#POTS - POTA = bits 0-7
#POTS - POTB = bits 8-15

#CUR_CTRL - bits 0-7, current control, given in tenths of amps

#DEV_CTRL
M_A_VEL               = 0 #Motor A 'velocity' (only works with 0 (don't move) or 1 (fully on)
M_A_DIR               = 1 #Motor A direction: 1 = forward; 0 = reverse
M_B_VEL               = 2 #Motor B 'velocity' (only works with 0 (don't move) or 1 (fully on)
M_B_DIR               = 3 #Motor B direction: 1 = forward; 0 = reverse
DEV_CTRL_4            = 4 #Spare/unused
SOL_A                 = 5 #Solenoid A control bit (0 = off, 1 = on)
SOL_B                 = 6 #Solenoid B control bit (0 = off, 1 = on)
SOL_CD                = 7 #Solenoid C & D control bit (0 = off, 1 = on)
M1_SAFE               = 8 #Determines whether the docking sensor prevents M1 (winch motor) from moving in upward direction if tripped. If high, safety enabled. If low, docking sensor is ignored when determining motor movement



#SETTINGS & LIMITS
MOTOR_CURRENT_MAX     = 14.0 #max allowed set current in amps
MOTOR_CURRENT_DEFAULT = 9.0 #Default initialize current limit