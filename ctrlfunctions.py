#imports
import sys
sys.path.insert(0, './config')
import time

import serial.tools.list_ports
from config import * #System-specific constants
import os
import sys
import time
import minimalmodbus

#i.e. given value 0x01001000 and position 3, returns 0x00001000 >> 3 = 1
def unbit(val, position):
  return (val & bit(1,position)) >> position

def bit(val, position):
  if (val > 1 or val < 0):
    print('warning: ran bit() function on value greater than 1')
    val = 0
  return val << position

##Creates string array of port items that match any of the tags in input string array portTagList
##From output array, use portsOut.device as the string input to the serial port name
def GetPorts(portTagList):
  ports = list(serial.tools.list_ports.comports())
  portsOut = []
  if (DEBUG): print 'Debugger Mode'
  if (DEBUG): print 'Matching Serial Ports:'
  for p in ports:
    for tag in portTagList:
      if tag in p.description: 
        portsOut.append(p)
        if (DEBUG): print p
  return portsOut

def RedundantWriteReg(instrument, registeraddress, value, numberOfDecimals=0, functioncode=16, signed=False):
  
  for i in range(COM_TRIES):
    try:
      instrument.write_register(registeraddress, value, numberOfDecimals, functioncode, signed)
      return
    except Exception as inst:
      #print type(inst)
      #print inst.args
      if (DEBUG): print inst
      if (DEBUG): print('Writing register %x failed at iteration %d' %(registeraddress, i))
  print('Com attempt limit reached. Exiting...')
  exit(-1)
      
def RedundantReadReg(instrument, registeraddress, numberOfDecimals=0, functioncode=3, signed=False):
  for i in range(COM_TRIES):
    try:
      val = instrument.read_register(registeraddress, numberOfDecimals, functioncode, signed)
      return val 
    except Exception as inst:
      if (DEBUG): print inst
      if (DEBUG): print('Reading register %x failed at iteration %d' %(registeraddress, i))
  
  print('Com attempt limit reached. Exiting...')  
  exit(-1)

def RedundantReadRegs(instrument, registeraddress, numRegisters, numberOfDecimals=0, functioncode=3, signed=False):
  for i in range(COM_TRIES):
    try:
      val = instrument.read_registers(registeraddress, numRegisters, functioncode)
      return val 
    except Exception as inst:
      if (DEBUG): print inst
      if (DEBUG): print('Reading register sequence starting at %x failed at iteration %d' %(registeraddress, i))
  
  print('Com attempt limit reached. Exiting...')  
  exit(-1)  
  #return instrument.read_registers(registeraddress, numRegisters, functioncode)


class Module:
  
  ##For initialization, port = serial port to use (string)
  #slave_address = address of slave device
  #If no port specified, possibly find it yourself?
  def __init__(self, slave_address, port=None):
    self.init_routine(slave_address, port)
    
  def init_routine(self, slave_address, userPort=None):
    if userPort == None: #Grab default serial port if not specified
      ports = GetPorts(COM_DEVICES)
      p = ports[0]
      portName = p.device
    else: portName = userPort    
    
    self.instrument = minimalmodbus.Instrument(portName, slave_address, MODBUS_MODE)
    self.instrument.serial.baudrate = MODBUS_BAUDRATE
    self.instrument.serial.timeout = MODBUS_TIMEOUT
    self.instrument.debug = False
    self.instrument.precalculate_read_size = True
  
  ##Writes to a register using supplied mask to mask which bits to change
  def ReadReg(self, register):
    return RedundantReadReg(self.instrument, register)
  def ReadRegs(self, register, numRegisters, functioncode=3):
    return RedundantReadRegs(self.instrument, register, numRegisters, functioncode)
  def WriteReg(self, register, val, mask=0xFFFF):
    if mask == 0xFFFF:
      RedundantWriteReg(self.instrument, register, val, 0, functioncode=6)
    else:
      orig_val = self.ReadReg(register)
      #if (DEBUG): print('orig. val = %04X' %orig_val);
      masked_val = (orig_val & ~(mask)) | val
      #if (DEBUG): print('masked val = %04X' %masked_val);
      RedundantWriteReg(self.instrument, register, masked_val, 0, functioncode=6)
  def GetLReg(self,register): #Get a locally stored register value
    if (time.clock() - self.refreshTime > MODBUS_MAX_REFRESH_PERIOD): #Must refresh local registers before accesssing
      self.Refresh()
    return self.registers[register]
  def GetLBit(self, register, pos): #Get locally stored bit value from register "register" and bit position "pos"
    r = self.GetLReg(register)
    return unbit(r, pos)
  
  
  #def ReadReg(self, register):
  #  return self.instrument.read_register(register)


class Module1(Module): ## Aux Board

  def __init__(self, port=None):
    self.init_routine(D1.ADDR, port)
    self.ADDR = D1.ADDR
    self.registers = self.ReadRegs(0x00, 3)
    self.refreshTime = time.clock()
  def Refresh(self):
    self.registers = self.ReadRegs(0x00, 3)
    self.refreshTime = time.clock()
  
  ##Sets a single  electromagnet on or off, based on state input and magnet channel input
  ##Magnet 1 - Docking magnet
  ##Magnet 2 - Grip magnet
  def SetMagnet(self, channel, state):
    if channel == 1: 
      mask = bit(1, D1.EM1)
      writeval = bit(state, D1.EM1)
    elif channel == 2: 
      mask = bit(1, D1.EM2)
      writeval = bit(state, D1.EM2)
    else: 
      print('Warning: Incorrect channel %d specified in routine SetMagnet(). Ignoring.' %(channel))
      return

    #if (DEBUG): print('SetMagnet() mask = %04X, writeval = %04X' %(mask, writeval))
    self.WriteReg(D1.CTRL, writeval, mask)
  
  ##Writes a sequence of magnet values. Allows arbitrary number of magnets, starting from magnet 1 and counting up
  ##User inputs array of magnet values, starting from magnet 1 and counting up (i.e. user inputs [1,0] for magnet 1 on, magnet 2 off
  ##Magnet 1 - Docking magnet
  ##Magnet 2 - Grip magnet
  def SetMagnets(self, in_array):
    writeval = 0x00
    mask = 0x00
    
    mags = [D1.EM1, D1.EM2] #list of magnet register pins on device
    for i in range(len(mags)):
      m = mags[i]
      writeval |= (in_array[i] << mags[i])
      mask |= bit(1, mags[i])
    
    self.WriteReg(D1.CTRL, writeval, mask)
    
  def SetMasterEnable(self, set_bit):
    self.WriteReg(D1.CTRL, set_bit << D1.PI_EN, bit(1, D1.PI_EN))
  
  def SetTestActive(self, set_bit):
    self.WriteReg(D1.CTRL, set_bit << D1.TEST_ACTIVE, bit(1, D1.TEST_ACTIVE))
  
  #Allows the user to set the grip release time delay, in milliseconds
  def SetGripReleaseTime(self, release_time):
    if (release_time > 2**16-1): 
      print('Invalid grip release time of ') + str(release_time) + ' specified.'
      exit(1)
    
    self.WriteReg(D1.GRIP_RELEASE_TIME, release_time)
    
  def ReadSTATUS(self, bitNum):
    regVal = self.ReadReg(self.instrument, D1.STATUS)
    return unbit(regval, bitNum)
    
  def ReadCTRL(self, bitNum):
    regVal = self.ReadReg(self.instrument, D1.CTRL)
    return unbit(regval, bitNum)
    
class Module2(Module): ## Motor Control Board
  
  def __init__(self, port=None):
    self.init_routine(D2.ADDR, port)
    self.ADDR = D2.ADDR
    self.registers = self.ReadRegs(0x00, 5)
    self.refreshTime = time.clock()
  def Refresh(self):
    self.registers = self.ReadRegs(0x00, 5)
    self.refreshTime = time.clock()
    
  ##Sets the state of the motor on given channel
  ##vel_dir provides on/off state and direction (1 = forward, 0 = no movement, -1 = reverse)
  def SetMotor(self, channel, vel_dir):
    if vel_dir == 1: 
      vel_bit = 1
      dir_bit = 1
    elif vel_dir == -1:
      vel_bit = 1
      dir_bit = 0
    else:
      vel_bit = 0
      dir_bit = 0
      
    if channel == 1:
      vel_bit = bit(vel_bit, D2.M_A_VEL)
      dir_bit = bit(dir_bit, D2.M_A_DIR)
      mask = (bit(1, D2.M_A_VEL) | bit(1, D2.M_A_DIR))
    elif channel == 2:
      vel_bit = bit(vel_bit, D2.M_B_VEL)
      dir_bit = bit(dir_bit, D2.M_B_VEL)
      mask = (bit(1, D2.M_B_VEL) | bit(1, D2.M_B_DIR))
    else:
      print('Warning: Set Motor attempt with vel_dir bit = %d and channel %d invalid. Ignoring call' %(vel_dir, channel))
      return
      
    self.WriteReg(D2.DEV_CTRL, (vel_bit | dir_bit), mask)

  ##Sets whether to use dock sensor as forward limit switch for motor 1
  ##on_off = 0 -> don't use; on_off = 1 -> use dock sensor as limit switch
  def SetMotorLim(self, on_off):
    mask = bit(1,D2.M1_SAFE)
    writeval = bit(on_off, D2.M1_SAFE)
    self.WriteReg(D2.DEV_CTRL, writeval, mask)
  ##Sets motor current limit. Input is current limit in amps
  def SetMotorCurrentLim(self, current_lim):
    if current_lim > D2.MOTOR_CURRENT_MAX:
      print('Warning: SetMotorCurrentLim() Call asked for current of %f. Max allowed is 14. Ignoring call.' %(current_lim))
      return
    write_val = int(current_lim * 10 + 0.5) #Convert to tenths of amps and round
    self.WriteReg(D2.CUR_CTRL, write_val)
    
  def SetSolenoid(self, channel, state):
    if channel == 1: #Solenoid A
      mask = bit(1, D2.SOL_A)
      writeval = bit(state, D2.SOL_A)
    elif channel == 2: #Solenoid B
      mask = bit(1, D2.SOL_B)
      writeval = bit(state, D2.SOL_B)
    elif channel == 3: #Solenoid C+D
      mask = bit(1, D2.SOL_CD)
      writeval = bit(state, D2.SOL_CD)
    else: 
      print('Warning: Incorrect channel %d specified in routine SetSolenoid(). Ignoring.' %(channel))
      return

    self.WriteReg(D2.DEV_CTRL, writeval, mask)
    
  def SetSolenoids(self, in_array):
    writeval = 0x00
    mask = 0x00
    
    solenoidss = [D2.SOL_A, D2.SOL_B, D2.SOL_CD] #list of magnet register pins on device
    for i in range(len(solenoids)):
      m = solenoids[i]
      writeval |= (in_array[i] << solenoids[i])
      mask |= bit(1, solenoids[i])
    
    self.WriteReg(D2.DEV_CTRL, writeval, mask)
      
      
  def ReadSTATUS(self, bitNum):
    regVal = self.ReadReg(self.instrument, D2.STATUS)
    return unbit(regval, bitNum)
    
  def ReadDEV_CTRL(self, bitNum):
    regVal = self.ReadReg(self.instrument, D2.CTRL)
    return unbit(regval, bitNum)
  
class Module3(Module): ## Sensor Board
  
  def __init__(self, port=None):
    self.init_routine(D3.ADDR, port)
    self.ADDR = D3.ADDR
    self.registers = self.ReadRegs(0x00, 5)
    self.refreshTime = time.clock()
  def Refresh(self):
    self.registers = self.ReadRegs(0x00, 5)
    self.refreshTime = time.clock()
  
  def TimerReset(self):
    self.WriteReg(D3.CTRL, bit(1, D3.TIMER_RST), bit(1, D3.TIMER_RST))
  
  def ReadTimer(self): 
    ta = self.ReadReg(D3.TIMEA)
    tb = self.ReadReg(D3.TIMEB)
    return ((ta << 16) | tb)
    
  def ReadSENSORS(self, bitNum):
    regVal = self.ReadReg(self.instrument, D3.SENSORS)
    return unbit(regval, bitNum)

  def ReadSTATUS(self, bitNum):
    regVal = self.ReadReg(self.instrument, D3.STATUS)
    return unbit(regval, bitNum)    

##Debug Routine
if __name__ == '__main__':
    list = GetPorts(['CH340'])
    
    print '\nListing found ports:'
    for p in list:
      print p
      
  #d2 = Module2()
  #print(aux.ReadSTATUS(D2.EN)) #Checks if enable bit set on d2