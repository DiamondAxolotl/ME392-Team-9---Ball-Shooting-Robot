import serial
import time
import numpy as np
from sendStringScript import sendString

axle_length = 149 * 10**(-3) # (m) 
D_wheel = 72 * 10**(-3) # (m)
counts_per_rev = 1440 # (counts/rev)
counts_per_deg = counts_per_rev / 360 # (counts/deg) 

def drive_motors(leftMotor,rightMotor):
    sendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(rightMotor)+'>',0.0001)

def turn(v,angle,ori):
    count_limit = counts_per_deg*np.rad2deg(angle)*axle_length/D_wheel
    if ori=='CW':
        drive_motors(v,-v)
    elif ori=='CCW':
        drive_motors(-v,v)
    # Need to find a nonblocking way to obtain encoder counts
    # Ideally don't even begin collecting encoder data in the arduino until it gets a signal from python telling it to do so

def main():
    ser=serial.Serial('/dev/ttyACM0',115200)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8')
                #ive just called 2 methods from the ser object, what do they do? read the documentation and find out!
            line=line.split(',')
        # left_count = int(line[0])
        # right_count = int(line[1])
        drive_motors(100,-100)



if __name__ == '__main__':
    main()