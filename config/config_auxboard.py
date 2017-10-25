##D1: AUX BOARD DEFINITIONS
"""(Copied from aux board .ino file)
/*Contains auxiliary functionality for system, including
 * -control of enable pin
 * -control of electromagnets
 * 
 * Control sequence for this module is as follows: Device boots up with electromagnets turned off. After booting up, the master device may turn electromagnets on and off
 * (even if device not enabled). Once the device is enabled and the TEST_ACTIVE bit has been set, the module is 'armed' to turn off electromagnet 2 with a specified time 
 * delay after the GRIP_RELEASE_SENSOR has been tripped. The time delay can be programmed through the GRIP_RELEASE_TIME register. The global enable signal is also 
 * controlled by this module. The PI_EN bit in the CTRL register must be set by the master device, and the GATE_SWITCH_SIG must be high (entrance gate must be closed) for the 
 * global enable signal to be set. The STATUS register bits TOP_TRIP_SENSOR, GATE_SWITCH_SIG, and GRIP_RELEASE_SENSOR are inputs from arduino. 
 * 
 * An example master control sequence is as follows:
 * -Set GRIP_RELEASE_TIME register to desired time delay in milliseconds
 * -Activate EM1 and EM2
 * -Close gripper
 * -User must ensure gate is closed
 * -Set PI_EN bit in control register
 * -Ensure that EN bit in status register is high
 * -Dock trolley
 * -Set TEST_ACTIVE bit in CTRL register
 * -Deactivate EM1 to drop trolley
 * -Trolley will pass through GRIP_RELEASE_SENSOR and EM2 will deactivate after given time delay from GRIP_RELEASE_SENSOR being tripped
 * -Turn off PI_EN bit to disable testing mode
 * 
 * Notes/considerations
 * -How will user ensure electromagnet is not deactivated when trolley is docked?
 * 
 */
 """

ADDR                = 0x01 #Device slave address


#Register Definitions
STATUS              = 0x00 #Contains status bits that are viewed by master
CTRL                = 0x01 #Contains control bits that are set/cleared by master
GRIP_RELEASE_TIME   = 0x02 #Contains 16-bit grip release time delay in microseconds, set by master
TIMER               = 0x03 #For debugging (times main loop iteration time)
COUNTER             = 0x03 #For debugging (number of main loop iterations elapsed)
DEBUG               = 0x05 #For debugging (arbitrary)


#STATUS register
EN                  = 0 #Global enable pin - required to enable electromagnets and all modules
TOP_TRIP_SENSOR     = 1 #Docking sensor state
GATE_SWITCH_SIG     = 2 #Gate open/closed sensor state 
GRIP_RELEASE_SENSOR = 3 #Grip release sensor state
GRIP_TRIPPED        = 4 #Flag that shows whether grip release sensor has been tripped after TEST_ACTIVE bit has been set (this flag is reset by setting TEST_ACTIVE again)

#CTRL register
PI_EN               = 0 #Master enable bit - set this bit to set EN bit.
TEST_ACTIVE         = 1 #Set this bit to start the trigger for the timed grip magnet release. 
EM1                 = 2 #Electromagnet 1 on/off control (normally docking magnet) 
EM2                 = 3 #Electromagnet 2 on/off control (normally grip release magnet)

#GRIP_RELEASE_TIME - 16-bit grip release time in milliseconds
#TIMER - Times loop cycle time
#COUNTER - counts number of loop cycles
#DEBUG = arbitrary debug use


#SETTINGS & LIMITS
GRIP_RELEASE_TIME_DEFAULT = 100 #Default time in milliseconds to release the grip release electromagnet after the grip release sensor is tripped when the grip release trigger (TEST_ACTIVE bit) is set. 