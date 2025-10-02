#!/usr/bin/env python3
import serial
import time
import numpy as np

from sendStringScript import sendString
leftMotor=int(100)
rightMotor=int(100)

# F = Far, M = Middle, L = Left, R = Right
BP_FL=int(1)
BP_L=int(1)
BP_ML=int(1) #a bump sensor that is unactivated starts at 1 (because they are pullups), hence why these are all one
BP_MR=int(1)
BP_R=int(1)
BP_FR=int(1)


if __name__ == '__main__':
    ser=serial.Serial('/dev/ttyACM0',115200)
    #every time the serial port is opened, the arduino program will restart, very convient!
    ser.reset_input_buffer()
    ready = 0
    

    while True:
        
        #think of the below line as the default condition where no pairs of sensors are triggered as state 0, where the robot moves forward
        sendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(rightMotor)+'>',0.0005)
        #ser.write(b'<'+bytes(str(leftMotor),'utf-8')+b','+bytes(str(rightMotor),'utf-8')+b'>')


        #why so I append '<' and '>' to the beginning and end of my message that I send to the arduino?
        # Because the start and end markers in the arduino code are delineated with the <> symbols

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8')
                #ive just called 2 methods from the ser object, what do they do? read the documentation and find out!
            line=line.split(',')
                #this one i wont ask you about this one is pretty self explanitory

            try:
                    
                BP_FL = int(line[0])
                BP_L = int(line[1])
                BP_ML = int(line[2])

                BP_MR = int(line[3])  
                BP_R = int(line[4])
                BP_FR = int(line[5])

                print([BP_FL, BP_L, BP_ML, BP_MR, BP_R, BP_FR])
                
            except:
                print("packetLost") 
                #why do I have this exepction? 



       
            #rudimentery state machine
         
        # Keep Driving
            
        # Avoid Head On Collision
        if BP_ML < 1 and BP_MR <1:
            sendString('/dev/ttyACM0',115200,'<'+str(-leftMotor)+','+str(-rightMotor)+'>',0.0005)
            time.sleep(2)
            sendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(rightMotor)+'>',0.0005)
            BP_ML = 1
            BP_MR = 1
            
        # # Avoid Right Obstacle
        if BP_FR < 1 and BP_R < 1:
            sendString('/dev/ttyACM0',115200,'<'+str(-leftMotor)+','+str(-rightMotor)+'>',0.0005)
            time.sleep(2)
            sendString('/dev/ttyACM0',115200,'<'+str(-leftMotor)+','+str(rightMotor)+'>',0.0005)
            time.sleep(2)
            BP_FR = 1
            BP_R = 1
        # # Avoid Left Obstacle
        if BP_FL < 1 and BP_L < 1:
            sendString('/dev/ttyACM0',115200,'<'+str(-leftMotor)+','+str(-rightMotor)+'>',0.0005)
            time.sleep(2)
            sendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(-rightMotor)+'>',0.0005)
            time.sleep(2)
            BP_FL = 1
            BP_L = 1
            
        # E-Stop Command
        if BP_FL < 1 and BP_FR < 1:
            sendString('/dev/ttyACM0',115200,'<'+str(0)+','+str(0)+'>',0.0005)
            break