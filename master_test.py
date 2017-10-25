""" 
Sean Coss
10-10-17
NMT/LANL Drop Tower Control Library

This code demonstrates the ability to control the drop tower circuitry using the minimalmodbus library and the control function wrappers that I wrote. The code refers to the .py files in the ./config folder for many of the configuration settings used. 

The code first selects the USB-RS485 serial adapter from a list of user-specified possible devices. Then, it instantiates and initializes three modules corresponding to the three microcontroller on the control panel. Next, the code begins the main test loop, which checks the inputs and sets ouputs at each test step corresponding to what each test step should do. The loop works like a finite state machine where only one section of the loop is entered at each loop iteration corresponding to the state the device is currently in. 

MinimalModbus: https://pypi.python.org/pypi/MinimalModbus/
*Note that it is necessary to edit the minimalmodbus.py file as follows:
minimalmodbus.py is installed in the site-packages folder under python if pip is used to install the packaage.
Open the file, browse to the _calculate_minimum_silent_period() function, and replace the value returned with 0.025. This 
waits longer between the time the arduino responds to a command and the time  the next command is sent. The code likely will not work correctly without this modification, and will have timeout errors. 
"""

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


#Instantiate module class objects. This opens serial communications with the modules, sets default baudrate
M1 = Module1(portName) #Aux Board (control of electromagnets, grip release timer, unused GPIO, global enable)
M2 = Module2(portName) #Motor Control Board (control of motors and solenoids)
M3 = Module3(portName) #Sensor Board (grip release sensor, velocity sensors, docking sensor, gate open/closed sensor)

if (DEBUG): print ('All instruments initialized')

#Debug routine - reads all relevant registers on all modules
if (DEBUG):
  start = time.clock()
  for i in range(10):
    val1 = [format(x, '08b') for x in M1.ReadRegs(0x00, 3)]
    val2 = [format(x, '08b') for x in M2.ReadRegs(0x00, 5)]
    val3 = [format(x, '08b') for x in M3.ReadRegs(0x00, 5)]
    print str(val1) + '\t' + str(val2) + '\t' + str(val3)
  stop = time.clock()
  print("dt = %f" %(stop-start))



state_init = True
activeRefresh = False #Determines whether to refresh module register values every loop iteration
state = POWER_INIT

  
if __name__ == '__main__': #"main" function - only runs if this file is run as a standalone python script (i.e. is run using command "python master_test.py") 
  while (1): #Enter "state machine". Each iteration of this loop will tkae place in one of the if statements that queries what "state" the device is currently in. 
    #Update the locally stored values of each module register by retrieving the most recent values from the microcontrollers. This saves time that would otherwise be used to access individual registers each time their values are needed.
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
        M2.SetMotorCurrentLim(D2.MOTOR_CURRENT_DEFAULT) #Set motor driver current limit to the default value given in config_mtrctrlboard.py 
        if (DEBUG): print ('Motor current lim set to %d deci-amps' %M2.ReadReg(D2.CUR_CTRL))
        M1.SetGripReleaseTime(D1.GRIP_RELEASE_TIME_DEFAULT) #Set time to release grip magnet after the grip trip sensor is tripped - default value given by config_auxboard.py
        if (DEBUG): print ('grip release time set to %d ms' %M1.ReadReg(D1.GRIP_RELEASE_TIME))
        state_init = False
      
      if (not M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)): # Check state of motor control switch bit by getting its locally stored value - MTR_CTRL_SW bit of STATUS register of motor control module
        state = USER_TEST_PREP #!!!only advance state if motor control switch set to "manual" mode
        state_init = True
      
    elif (state == USER_TEST_PREP):
      #System is in user test preparation mode. In this state, user manually adjusts winch,
      #pressurizes tanks, loads container into gripper. 
      #Top magnet does not turn on, gripper magnet does
      #State moves to AUTO_SYSTEM_CHECK if trolley not in docked position and motor control switch flips to off
      if (state_init):
        if (DEBUG): print('STATE: USER_TEST_PREP - Manual test setup steps')
        M1.SetMasterEnable(1) #Set the enable bit of aux module, enabling device (certain functionality like turning on electromagnets, turning on solenoids, automatically controlling motors relies on this bit being high)
        M1.SetMagnet(2, 1) #energize grip release magnet
        state_init = False
      #print 'USER_TEST_LOOP'
      
      
      #Advance state when motor control switch set to automatic and docking sensor unblocked 
      if (M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW) and M2.GetLBit(D2.STATUS, D2.TOP_TRIP_SENSOR)): 
        state = AUTO_SYSTEM_CHECK
        state_init = True
        
    elif (state == AUTO_SYSTEM_CHECK):
    #In this state, system runs check to make sure all sensors are unblocked. State advances when all sensors (grip release sensor, docking sensor, velocity sensors) unblocked and gate sensor is closed and manual motor control switch is off
      if (state_init):
        state_init = False
        if (DEBUG): print('STATE: AUTO_SYSTEM_CHECK - System checks before docking trolley')
        
        
      #Store sensor and switch values to variables for later use in the loop
      _dock_sensor          = M3.GetLBit(D3.SENSORS,D3.TOP_TRIP_SENSOR)
      _grip_rel_sensor      = M3.GetLBit(D3.SENSORS,D3.GRIP_RELEASE_SENSOR)
      _top_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.TOP_VEL_SENSOR)
      _btm_vel_sensor       = M3.GetLBit(D3.SENSORS,D3.BTM_VEL_SENSOR)
      _gate_state           = M3.GetLBit(D3.SENSORS,D3.GATE_SWITCH_SIG)
      _usr_ctrl_sw          = M2.GetLBit(D2.STATUS, D2.MTR_CTRL_SW)
      
      #Check sensor and switch values to determine whether system may advance states
      if (_dock_sensor and _grip_rel_sensor and _top_vel_sensor and _btm_vel_sensor and _gate_state and _usr_ctrl_sw):
        state = AUTO_DOCK_TROLLEY
        state_init = True
        
    elif (state == AUTO_DOCK_TROLLEY):
    #In this state, the system automatically docks the trolley by energizing the docking electromagnet, raising the winch until the docking sensor is tripped, lowering the winch for stage1_time, and raising the winch for stage2_time. 
    #Note this does not check if trolley has become undocked during stage 2 (the stage where the winch is lowered to release the shackle from the trolley). It may be important to check if this occurs before preceeding from stage 2. 
      if (state_init):
        state_init = False
        if (DEBUG): print('STATE: AUTO_DOCK_TROLLEY - System automatically docks trolley')
        M1.SetMagnet(1,1) #Turn on dock magnet
        dock_stage = 0
        dock_stage_init = 1
        #stage0 - winch lifts trolley until docking sensor tripped
        #stage1 - winch lowers cable, releasing shackle from trolley
        #stage2 - winch lifts cable, clearing it from trolley
        
        stage1_time = 1 #stage1 lower time, seconds
        stage2_time = 2 #stage2 lift time, seconds
        
      #perform non-blocking dock procedure
      if (dock_stage == 0):
        if (dock_stage_init):
          dock_stage_init = False
          M2.SetMotor(1, 1) #begin lifting motor
        
        _dock_sensor          = M3.GetLBit(D3.SENSORS,D3.TOP_TRIP_SENSOR) #Update dock sensor state
        if (not _dock_sensor): # Proceed once docking sensor is tripped
          M2.SetMotor(1,0) #stop lifting motor once sensor tripped
          dock_stage = 1
          dock_stage_init = True
          
      elif (dock_stage == 1): #Lower winch to release shackle
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
    #This state checks to make sure all system inputs read values that show that the system is ready to go. This includes
    #-Docking sensor tripped, other photosensors not tripped
    #-Gate open sensor is closed
    #-Manual motor control switch set to auto
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
        
        #Expected responses from user query
        yes = True
        Yes = True
        YES = True
        y = True
        Y = True
        no = False
        
        usr_in = input('All systems ready to begin test. Begin? (yes/no): ') #Take user input (should be a yes or a no) to determine whether to begin test
        
        if (usr_in):
          state = START_TEST
          state_init = True
          
    elif (state == START_TEST):
    #This state sets appropriate system states to active, fires the acceleration solenoids, and turns off the dock magnet. 
      if (state_init):
        state_init = False
        if (DEBUG): print('State: START_TEST - System Beginning Test...')
        M1.SetTestActive(1) #Activate timed grip release trigger - required for automatic timed grip release
        M3.TimerReset() #Reset velocity sensor timer - prepares sensorboard module to record time of travel through the velocity sensors
        M3.Refresh()
        if (DEBUG): print('Timer Active State = %d' %M3.GetLBit(D3.STATUS,D3.TIMER_ACTIVE))
        if (DEBUG): print('Test Ready State = %d' %M3.GetLBit(D3.STATUS,D3.TEST_READY))
        if (DEBUG): print('Activating Solenoids & Dropping Trolley...')
        M2.SetSolenoid(3,1) #Turn on Solenoids C + D (solenoid 1=A, 2=B, 3=(C+D))
        M1.SetMagnet(1,0) #Turn off dock magnet
        
        state = TEST_IN_PROGRESS
        state_init = True
        
    elif (state == TEST_IN_PROGRESS):
    #This state causes a 10-second pause before entering the next state
      if (state_init):
        state_init = False
        if (DEBUG): print('State: TEST_IN_PROGRESS - System does nothing for specified time...')
        time.sleep(10) #Sleep for 10 seconds
        
      state = POST_TEST
      state_init = True
      
    elif(state == POST_TEST):
    #This state turns off solenoids and reads the time value that was recorded by the sensorboard module timer. 
      if (state_init): 
        state_init = False
        if (DEBUG): print('State: POST_TEST - Test finished, displaying results & cleaning up')
        M2.SetSolenoid(3,0) #Turn off Solenoids C + D (solenoid 1=A, 2=B, 3=(C+D))
        
        _vel_time = M3.ReadTimer() #Get velocity time reading (should be in microseconds)
        print('Velocity time = %d microseconds' %_vel_time)
        
      state = BREAK
      state_init = True
        
      
    else:
      break

   