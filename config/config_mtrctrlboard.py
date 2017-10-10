##D2: MOTOR CONTROL BOARD DEFINITIONS

ADDR                  = 0x02 #Device slave address

#Register Definitions
STATUS                = 0x00
POTS                  = 0x01
CUR_CTRL              = 0x02
TORQUE                = 0x03
DEV_CTRL              = 0x04
TIMER                 = 0x05
COUNTER               = 0x06
DEBUG                 = 0x07

#STATUS register
EN                    = 0
TOP_TRIP_SENSOR       = 1
MTR_CTRL_SW           = 2 #Active low
M_A1                  = 3
M_A2                  = 4
M_B1                  = 5
M_B2                  = 6
SPI_ERR0              = 7
SPI_ERR1              = 8
SPI_ERR2              = 9
SPI_ERR3              = 10

#POTS - POTA = bits 0-7
#POTS - POTB = bits 8-15

#CUR_CTRL - bits 0-7, current control, given in tenths of amps

#DEV_CTRL
M_A_VEL               = 0
M_A_DIR               = 1
M_B_VEL               = 2
M_B_DIR               = 3
DEV_CTRL_4            = 4 #Spare/unused
SOL_A                 = 5
SOL_B                 = 6
SOL_CD                = 7
M1_SAFE               = 8



#SETTINGS & LIMITS
MOTOR_CURRENT_MAX     = 14.0 #max allowed set current in amps
MOTOR_CURRENT_DEFAULT = 9.0 #Default initialize current limit