##D1: AUX BOARD DEFINITIONS

ADDR                = 0x01 #Device slave address


#Register Definitions
STATUS              = 0x00
CTRL                = 0x01
GRIP_RELEASE_TIME   = 0x02
TIMER               = 0x03
COUNTER             = 0x03
DEBUG               = 0x05


#STATUS register
EN                  = 0
TOP_TRIP_SENSOR     = 1
GATE_SWITCH_SIG     = 2
GRIP_RELEASE_SENSOR = 3
GRIP_TRIPPED        = 4

#CTRL register
PI_EN               = 0
TEST_ACTIVE         = 1
EM1                 = 2
EM2                 = 3

#GRIP_RELEASE_TIME - 16-bit grip release time in milliseconds
#TIMER - Times loop cycle time
#COUNTER - counts number of loop cycles
#DEBUG = arbitrary debug use


#SETTINGS & LIMITS
GRIP_RELEASE_TIME_DEFAULT = 100