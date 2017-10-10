##D3: SENSOR BOARD DEFINITIONS

ADDR                  = 0x03 #Device slave address

#Register Definitions
SENSORS               = 0x00   
TIMEA                 = 0x01
TIMEB                 = 0x02
STATUS                = 0x03
CTRL                  = 0x04


#SENSORS0 register
TOP_TRIP_SENSOR       = 0
GRIP_RELEASE_SENSOR   = 1
MISC_1_SENSOR         = 2
MISC_2_SENSOR         = 3
TOP_VEL_SENSOR        = 4
BTM_VEL_SENSOR        = 5
GATE_SWITCH_SIG       = 6


#TIMEA register - MSB of velocity sensor timer
#TIMEB register - LSB of velocity sensor timer

#STATUS register
TIMER_ACTIVE          = 0
TEST_READY            = 1
TIMER_TRIPPED         = 2

#CTRL register
TIMER_RST             = 0