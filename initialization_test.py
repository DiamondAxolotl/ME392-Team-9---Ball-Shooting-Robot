import RPi.GPIO as GPIO
import time
import serial
from sendStringScript import sendString

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

def main():
    ser=serial.Serial('/dev/ttyACM0',115200)
    ser.reset_input_buffer() #clears anything the arduino has been sending while the Rpi isnt prepared to recieve.
    print(f"Distance: {distance()} CM")
    time.sleep(1)
    print(f"Distance: {distance()} CM")
    GPIO.cleanup()
    drive_motors(100,100)

if __name__ == '__main__':
    main()