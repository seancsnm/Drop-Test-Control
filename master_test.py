from ctrlfunctions import *
import time 


#Sequence State Enumeration
POWER_INIT          = 0
USER_TEST_PREP      = 1
AUTO_SYSTEM_CHECK   = 2
AUTO_DOCK_TROLLEY   = 3
AUTO_FINAL_CHECK    = 4
START_TEST          = 5
TEST_IN_PROGRESS    = 6
POST_TEST           = 7
SYS_RESET           = 8
BREAK               = 999
 



#Select comm port
port_list = GetPorts(COM_DEVICES)
port = port_list[0] #Assume first matching port is valid port
portName = port.device
if (DEBUG): print ('Using port ') + port.description
#print (port.device)

print ("YOLO")

#Initialize serial communication
M1 = Module1(portName) #Aux Board
M2 = Module2(portName) #Motor Control Board
M3 = Module3(portName) #Sensor Board

if (DEBUG): print ('All instruments initialized')



start = time.clock()
for i in range(10):
  val1 = [format(x, '08b') for x in M1.ReadRegs(0x00, 3)]
  #print ('val 1 = ' + str(val1))
  #print strval1
  val2 = [format(x, '08b') for x in M2.ReadRegs(0x00, 5)]
  #print ('val2 = ' + str(val2))
  val3 = [format(x, '08b') for x in M3.ReadRegs(0x00, 5)]
  #print ('val3 = ' + str(val3))
  #M2.SetMotorCurrentLim(D2.MOTOR_CURRENT_DEFAULT+i)
  
  
  #print('starting read')
  #print(M2.ReadReg(D2.CUR_CTRL))
  #print('now write %d' %i)
  #time.sleep(1)
  #M2.WriteReg(D2.CUR_CTRL, i)
  #time.sleep(1)
  
  #print M1.ReadReg(D1.CTRL)
  #print('read')
  #M1.WriteReg(D1.CTRL, 0b1000)
  
 
  
  
  print str(val1) + '\t' + str(val2) + '\t' + str(val3)
  #time.sleep(0.02)
  #print ("%s\t%s\t%s", %
  #print val2
  #val3 = M3.ReadReg(D3.SENSORS)
  #print('%s\t%s\t%s\t' %(format(val1, '016b'), format(val2, '016b'), format(val3, '016b')))
stop = time.clock()

print("dt = %f" %(stop-start))



state_init = True
activeRefresh = False #Determines whether to refresh module register values every iteration
state = POWER_INIT

  
if __name__ == '__main__': #"main" function  
  while (1):
    #Update the local values of each module by retrieving the most recent values from the microcontrollers
    if (activeRefresh):
      M1.Refresh()
      M2.Refresh()
      M3.Refresh()
    
   
    # print format(M1.registers[D1.STATUS], '016b')
    # print format(M2.registers[D2.STATUS], '016b')
    # print format(M3.registers[D3.STATUS], '016b')
      
    # print ("M2 top trip sensor status = %d" %(M2.GetLBit(D2.STATUS, D2.TOP_TRIP_SENSOR)))
    
    # while (1):
      # print ("M2 MTR CTRL SW status = %d" %(M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)))
    
      
      
    if (state == POWER_INIT):
    #System is powered on for first time. May be replaced with SYS_RESET
      if (state_init):
        if (DEBUG): print('STATE: POWER_INIT; Power-on Initialization')
        M2.SetMotorCurrentLim(D2.MOTOR_CURRENT_DEFAULT)
        if (DEBUG): print ('Motor current lim set to %d deci-amps' %M2.ReadReg(D2.CUR_CTRL))
        M1.SetGripReleaseTime(D1.GRIP_RELEASE_TIME_DEFAULT)
        if (DEBUG): print ('grip release time set to %d ms' %M1.ReadReg(D1.GRIP_RELEASE_TIME))
        state_init = False
      
      if (not M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)):
        state = USER_TEST_PREP #!!!only advance state if motor control switch set to "manual" mode
        state_init = True
      
    elif (state == USER_TEST_PREP):
      #System is in user test preparation mode. In this state, user manually adjusts winch,
      #pressurizes tanks, loads container into gripper. 
      #Top magnet does not turn on, gripper magnet does
      #State moves to AUTO_SYSTEM_CHECK if trolley not in docked position and motor control switch flips to off
      if (state_init):
        if (DEBUG): print('STATE: USER_TEST_PREP - Manual test setup steps')
        M1.SetMasterEnable(1) #Master-side enable of device
        M1.SetMagnet(2, 1) #turn on gripper magnet
        state_init = False
      #print 'USER_TEST_LOOP'
      
      
      #Advance state when motor control switch set to automatic and docking sensor unblocked 
      if (M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW) and M2.GetLBit(D2.STATUS, D2.TOP_TRIP_SENSOR)): 
        state = AUTO_SYSTEM_CHECK
        state_init = True
        
    elif (state == AUTO_SYSTEM_CHECK):
    #Make sure all sensors are unblocked, proceed when all sensors unblocked and gate closed and manual motor control off
      if (state_init):
        state_init = False
        if (DEBUG): print('STATE: AUTO_SYSTEM_CHECK - System checks before docking trolley')
        
        
      _dock_sensor          = M3.GetLBit(D3.SENSORS,D3.TOP_TRIP_SENSOR)
      _grip_rel_sensor      = M3.GetLBit(D3.SENSORS,D3.GRIP_RELEASE_SENSOR)
      _top_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.TOP_VEL_SENSOR)
      _btm_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.BTM_VEL_SENSOR)
      _gate_state           = M3.GetLBit(D3.SENSORS,D3.GATE_SWITCH_SIG)
      _usr_ctrl_sw          = M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)
      if (_dock_sensor and _grip_rel_sensor and _top_vel_sensor and _btm_vel_sensor and _gate_state and _usr_ctrl_sw):
        state = AUTO_DOCK_TROLLEY
        state_init = True
        
    elif (state == AUTO_DOCK_TROLLEY):
      if (state_init):
        state_init = False
        if (DEBUG): print('STATE: AUTO_DOCK_TROLLEY - System automatically docks trolley')
        M1.SetMagnet(1,1) #Turn on dock magnet
        dock_stage = 0
        dock_stage_init = 1
        #stage0 - winch lifts trolley until docking sensor tripped
        #stage1 - winch lowers cable, releasing shackle from trolley
        #stage2 - winch lifts cable, clearing it from trolley
        
        stage1_time = 1 #stage1 lift time, seconds
        stage2_time = 2 #stage2 lower time, seconds
        
      #perform non-blocking dock procedure
      if (dock_stage == 0):
        if (dock_stage_init):
          dock_stage_init = False
          M2.SetMotor(1, 1) #begin lifting motor
        
        _dock_sensor          = M3.GetLBit(D3.SENSORS,D3.TOP_TRIP_SENSOR)
        if (not _dock_sensor):
          M2.SetMotor(1,0) #stop lifting motor once sensor tripped
          dock_stage = 1
          dock_stage_init = True
          
      elif (dock_stage == 1):
        if (dock_stage_init):
          dock_stage_init = False
          M2.SetMotor(1, -1) #begin lowering motor
          t_start = time.clock() #Begin recording lower time
        
        if (time.clock() - t_start > stage1_time): #when to stop stage1
          M2.SetMotor(1,0) #stop lowering motor
          dock_stage = 2
          dock_stage_init = True
          
      elif (dock_stage == 2):
        if (dock_stage_init):
          dock_stage_init = False
          M2.SetMotor(1,1) #begin raising motor
          t_start = time.clock() #begin recording stage2 time
          
        if (time.clock() - t_start > stage2_time): #when to stop stage2
          M2.SetMotor(1,0) #stop raising motor
          dock_stage = 3
          dock_stage_init = True
          
      else:
        state = AUTO_FINAL_CHECK
        state_init = True
        
    elif (state == AUTO_FINAL_CHECK):
      if (state_init):
        state_init = False
        if (DEBUG): print('State: AUTO_FINAL_CHECK - System performs final checks before test begins')
      
      _dock_sensor          = M3.GetLBit(D3.SENSORS,D3.TOP_TRIP_SENSOR)
      _grip_rel_sensor      = M3.GetLBit(D3.SENSORS,D3.GRIP_RELEASE_SENSOR)
      _top_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.TOP_VEL_SENSOR)
      _btm_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.BTM_VEL_SENSOR)
      _gate_state           = M3.GetLBit(D3.SENSORS,D3.GATE_SWITCH_SIG)
      _usr_ctrl_sw          = M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)
      if ((not _dock_sensor) and _grip_rel_sensor and _top_vel_sensor and _btm_vel_sensor and _gate_state and _usr_ctrl_sw):
        yes = True
        Yes = True
        YES = True
        y = True
        Y = True
        no = False
        usr_in = input('All systems ready to begin test. Begin? (yes/no): ')
        
        if (usr_in):
          state = START_TEST
          state_init = True
          
    elif (state == START_TEST):
      if (state_init):
        state_init = False
        if (DEBUG): print('State: START_TEST - System Beginning Test...')
        M1.SetTestActive(1) #Activate timed grip release trigger
        M3.TimerReset() #Reset velocity sensor timer - prepares it to record time
        M3.Refresh()
        if (DEBUG): print('Timer Active State = %d' %M3.GetLBit(D3.STATUS,D3.TIMER_ACTIVE))
        if (DEBUG): print('Test Ready State = %d' %M3.GetLBit(D3.STATUS,D3.TEST_READY))
        if (DEBUG): print('Activating Solenoids & Dropping Trolley...')
        M2.SetSolenoid(3,1) #Turn on Solenoids C + D
        M1.SetMagnet(1,0) #Turn off dock magnet
        
        state = TEST_IN_PROGRESS
        state_init = True
        
    elif (state == TEST_IN_PROGRESS):
      if (state_init):
        state_init = False
        if (DEBUG): print('State: TEST_IN_PROGRESS - System does nothing for specified time...')
        time.sleep(10) #Sleep for 10 seconds
        
      state = POST_TEST
      state_init = True
      
    elif(state == POST_TEST):
      if (state_init): 
        state_init = False
        if (DEBUG): print('State: POST_TEST - Test finished, displaying results & cleaning up')
        M2.SetSolenoid(3,0) #Turn off solenoids C + D
        
        _vel_time = M3.ReadTimer() #Get velocity time reading
        print('Velocity time = %d us' %_vel_time)
        
      state = BREAK
      state_init = True
        
      
    else:
      break
    #Begin state machine

  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  