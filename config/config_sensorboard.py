##D3: SENSOR BOARD DEFINITIONS
"""Copied from IR_Board1 ino:
/*Contains the Arduino Uno/atmega328 code for the board which controls the photogate and personnel gate open/closed sensors on the tower. 
 * This board has support for 6 photogate sensors that are high when open, and low when blocked. 
 
 *  Time data is in microseconds and is stored in the TIMEA (MSB) and TIMEB (LSB) registers
 *  
 *  The recommended master-side sequence for running the module in a test setting is as follows:
 *  0) User ensures that no sensors are blocked, and that trolley is docked and ready to go
 *  1) Master device sets the TIMER_RST bit to activate the timer
 *  2) Master device checks the TEST_READY bit to ensure that all sensors are blocked/unblocked appropriately, and that the timer has been activated
 *  3) Master runs test and waits approximate time it takes for drop test to complete, plus 1 second to give the microcontroller time to save data to memory
 *  4) Master checks TIMER_TRIPPED bit to ensure that timer was tripped succesfully
 *  5) Master retrieves data from registers TIMEA and TIMEB, and re-assembles the time value; checks value to ensure it makes sense
 *  6) Start again at (0) for repeated tests
 *
 */
 """

ADDR                  = 0x03 #Device slave address

#Register Definitions
SENSORS               = 0x00 #Contains most of the system sensor states, viewed by master
TIMEA                 = 0x01 #Contains MSBs of the velocity sensor time measurement, viewed by master
TIMEB                 = 0x02 #Contains LSBs of the velocity sensor time measurement, viewed by master
STATUS                = 0x03 #Status of the system, viewed by master
CTRL                  = 0x04 #Contains control bits that are set/cleared by master


#SENSORS0 register
TOP_TRIP_SENSOR       = 0 #Docking sensor state (low when tripped)
GRIP_RELEASE_SENSOR   = 1 #Grip release sensor state (low when tripped)
MISC_1_SENSOR         = 2 #Reserved
MISC_2_SENSOR         = 3 #Reserved
TOP_VEL_SENSOR        = 4 #Top velocity chronograph sensor/first to be tripped
BTM_VEL_SENSOR        = 5 #Bottom velocity chronograph sensor/second to be tripped
GATE_SWITCH_SIG       = 6 #Personel access gate open/closed sensor state (high when gate closed)


#TIMEA register - MSB of velocity sensor timer
#TIMEB register - LSB of velocity sensor timer

#STATUS register
TIMER_ACTIVE          = 0 #Determines whether the velocity sensors are ready to start/stop the timer when they are tripped in succession
TEST_READY            = 1 #high when the chronograph is active and ready to take a velocity measurement
TIMER_TRIPPED         = 2 #high when the timer has moved from an active/ready state to a "tripped" state, or a measurement complete state

#CTRL register
TIMER_RST             = 0 #Set to 1 to reset and/or set the timer to its active state. Before setting this bit, ensure that the previous time measurement has been successfully recovered by the master device