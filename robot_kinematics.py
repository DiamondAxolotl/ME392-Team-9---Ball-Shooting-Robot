import serial
import RPi.GPIO as GPIO
import time
import numpy as np
from sendStringScript import sendString

axle_length = 149 * 10**(-3) # (m) 
D_wheel = 72 * 10**(-3) # (m)
counts_per_rev = 1440 # (counts/rev)
counts_per_deg = counts_per_rev / 360 # (counts/deg) 

ser=serial.Serial('/dev/ttyACM0',115200)

TRIG = 4
ECHO = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

def distance():
    GPIO.output(TRIG, False)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) ==0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance= pulse_duration * 17150
    distance = round(distance, 2)
    return distance

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

def turnN(angle):
    kp = 0.5
    lookup = dict()
    curr_ang = 0.0
    line = ser.readline().decode('utf-8')
    line=[i.strip() for i in line.split(',')]
    startVal = float(line[2])
    err = abs(startVal - float(line[2])) - angle
    while (err > 25) or (err < -25):
        print(err)
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8')
                line=[i.strip() for i in line.split(',')]
                err = abs(startVal - float(line[2])) - angle
                # print(line)
                curr_ang = startVal - float(line[2])
                # print(curr_ang)
        except:
            continue
        dist = distance()
        # print(dist)
        lookup[curr_ang] = dist
        drive_motors(err*kp,-err*kp)
    return lookup


def main():
    
    ser.reset_input_buffer() 
    lookup = turnN(360)
    drive_motors(0,0)
    print(lookup)
    
    res = -min(lookup, key=lookup.get)
    print(res)
    time.sleep(3)
    print("slept")
    turnN(res)
    print("donzo")
    # while True:
    #     if ser.in_waiting > 0:
    #         line = ser.readline().decode('utf-8')
    #             #ive just called 2 methods from the ser object, what do they do? read the documentation and find out!
    #         line=[i.strip() for i in line.split(',')]
    #         print(line)
        # left_count = int(line[0])
        # right_count = int(line[1])




if __name__ == '__main__':
    main()