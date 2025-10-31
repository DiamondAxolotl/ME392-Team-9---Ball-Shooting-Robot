
#include <AStar32U4Motors.h>
#include <Encoder.h>

AStar32U4Motors m; //read the documentation of this library to understand what functions to use to drive the motors and how to use them

#define PI 3.141592653589

int leftMotor; // COMMANDED MOTOR SPEEDS
int rightMotor;

double leftMotorMax = 28.86; // pur max values
double rightMotorMax = 28.86;

const int encoderRightPinA = 0;
const int encoderRightPinB = 1;

const int encoderLeftPinA = 3; 
const int encoderLeftPinB = 2;

Encoder encoderRight(encoderRightPinA,encoderRightPinB);
Encoder encoderLeft(encoderLeftPinA,encoderLeftPinB);

int encoderResolution = 1440; // counts per rev
double d = 2.7559055; //wheel diameter in inches

double encoderInterval = 10; // 10ms means 100Hz loop

int posLeftCount = 0;
int posRightCount = 0;
int posLeftCountLast = 0;
int posRightCountLast = 0;
double angle = 0.0; //angle of thing
double posLeftRad = 0.0; // this will need to be converted to rad/sec
double posRightDeg = 0.0; // this will need to be converted to rad/sec
double posLeftDeg = 0.0; // this will need to be converted to deg
double posRightRad = 0.0; // this will be converted to deg
double velLeft = 0; // this will be omegaLeft*d/2;
double velRight = 0; // this will be omegaRight*d/2 will be in inches per sec;
double newVelLeft = 0; // this will be omegaLeft*d/2;
double newVelRight = 0; // this will be omegaRight*d/2 will be in inches per sec;

// MOTOR LOOP CONSTANTS
double interval = 5.0; // 5 ms means 200Hz loop
unsigned long previousMillis = 0;
unsigned long priorTimeL,priorTimeR; // We need to keep track of time for each PID controller separately
double lastSpeedErrorL,lastSpeedErrorR; //same with error
double cumErrorL, cumErrorR;
double maxErr = 20; // chosen arbitrarily for now, students can tune. 
double desVelL = 10; // will be in inches per sec
double desVelR = 10;

// PID CONSTANTS
// LEFT MOTOR - you need to find values. FYI I found good responses with Kp ~ 10x bigger than Ki, and ~3x bigger than Kd. My biggest value was <2.
double kpL = 1.0;
double kiL = 0.5;
double kdL = 0.1;
// Right MOTOR - assumes we need to tune them differently
double kpR = 1.0;
double kiR = 0.5;
double kdR = 0.1;    

// Send Rev Data
const byte numChars = 32;
char receivedChars[numChars];
char tempChar[numChars]; // temporary array used for parsing
boolean newData = false;

void setup() {
  Serial.begin(115200);
  commandMotors(0,0);
}

void loop() {
  // Non Blocking PID Control Loop
  unsigned long currentMillis = millis();

      posRightCount = encoderRight.read(); 
      posLeftCount = encoderLeft.read();

//   if (currentMillis - previousMillis >= interval){
//  
//     posRightRad = (posRightCount-posRightCountLast)/(interval/1000)*2*PI/1440 ; // Write expression to get Rad/sec. Pi is defined above FYI.
//     posLeftRad = (posLeftCount-posLeftCountLast)/(interval/1000)*2*PI/1440 ; // Same - Rad/sec
//     velRight = d/2*posRightRad; // Now convert to get inches/sec (tangential velocity)
//     velLeft = d/2*posLeftRad; // Same - Inches/sec
//
//     newVelRight = drivePIDR(velRight);
//     newVelLeft = drivePIDL(velLeft);
//     rightMotor = motorVelToSpeedCommand(newVelRight,rightMotorMax); //Ignoring PID. change to newVelRight
//     leftMotor = motorVelToSpeedCommand(newVelLeft,leftMotorMax); //Ignoring PID, change to newVelLeft
//      
//     
//     posRightCountLast = posRightCount;
//     posLeftCountLast = posLeftCount;
//
//     commandMotors(rightMotor,leftMotor);
//   }

   if (currentMillis - previousMillis >= encoderInterval){
      previousMillis = currentMillis;

      posRightDeg = (posRightCount/4) ; // Degree of wheel rotation
      posLeftDeg = (posLeftCount/4) ;
      angle = (posRightDeg / 1.666);
      
      Serial.print(posLeftDeg);
      Serial.print(",");
      Serial.print(posRightDeg);
      Serial.print(",");
      Serial.println(angle);
   }

  recvWithStartEndMarkers();

  // Parcing for Recived Motor Values
  if (newData == true){
    
    strcpy(tempChar, receivedChars); //make a copy of recievedChars so we can make changes to it and not change recievedChars 
    parseData();  

    newData = false;
    
  }
}

//=========================================================


void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
                                                               
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();
                                                             
                                                                  
        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminates the string, frankly unsure why I need this
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

////==================================================================

void parseData(){

  //once the data has been recieved, this function turns those charichters into ints that are then sent to the motors. 



  char *strtokIndexer; //doing char * allows strtok to increment across my string properly frankly im not sure why... my kingdom for a proper c++ class

  
  strtokIndexer = strtok(tempChar,","); //sets strtokIndexer = to everything up to the first comma in tempChar /0 //this line is broken
  leftMotor = atoi(strtokIndexer); //converts strtokIndexer into a int
  

  strtokIndexer= strtok(NULL, ","); //setting the first input to null causes strtok to continue looking for commas in tempChar starting from where it left off, im not really sure why 
  rightMotor = atoi(strtokIndexer);
  

  


  //now that we have extracted the data from the Rpi as floats, we can use them to command actuators somewhere else in the code
  commandMotors(leftMotor, rightMotor);
}

//============================================

void commandMotors(int l_m, int r_m){  

  //read the documentation for the functions that drive the motors in the astar library

  m.setM1Speed(r_m);
  m.setM2Speed(l_m);
  //uncomment to drive motors
}
//============================================


void SendEncoderData(){
  posRightCount = encoderRight.read(); 
  posLeftCount = encoderLeft.read();

}

//======= PID =========
double drivePIDL(double curr){
    double rateError;
    double error;
    unsigned long currentTime;
    unsigned long elapsedTime;
  
    currentTime = millis();                               //get current time
    elapsedTime = (double)(currentTime - priorTimeL);     // compute elasped time for this control period

    error = desVelL - curr;                               // Error
    cumErrorL += error*elapsedTime;                       // Cumulative Error(since we add this outside the loop, needs to be unique to the motor controlled)

    // INTEGRAL WINDUP                                    // REMOVE WINDUP
    if(cumErrorL>maxErr)
    cumErrorL = maxErr;
    else if (cumErrorL<-1*maxErr)
      cumErrorL = -1*maxErr;

    rateError = (error-lastSpeedErrorL)/elapsedTime;      // Derivative Error

    double out = kpL*error+kiL*cumErrorL+kdL*rateError;   // PID output

    lastSpeedErrorL = error;                              // remember current error
    priorTimeL = currentTime;                             // remember current time
    return out;                                           // return the needed motor speed. 
}
double drivePIDR(double curr){
    double rateError;
    double error;
    unsigned long currentTime;
    unsigned long elapsedTime;
  
    currentTime = millis();                               //get current time
    elapsedTime = (double)(currentTime - priorTimeR);      // compute elasped time for this control period

    error = desVelR - curr;                                   // Error
    cumErrorR += error*elapsedTime;                       // Cumulative Error(since we add this outside the loop, needs to be unique to the motor controlled)

    // INTEGRAL WINDUP                                    // REMOVE WINDUP
    if(cumErrorR>maxErr)
    cumErrorR = maxErr;
    else if (cumErrorR<-1*maxErr)
      cumErrorR = -1*maxErr;

    rateError = (error-lastSpeedErrorR)/elapsedTime;      // Derivative Error

    double out = kpR*error+kiR*cumErrorR+kdR*rateError;   // PID output

    lastSpeedErrorR = error;                              // remember current error
    priorTimeR = currentTime;                             // remember current time
    return out;                                           // return the needed motor speed. 
}

int motorVelToSpeedCommand(double Vel, double maxVel){
    int newSpeed = 0;
    Vel = constrain(Vel,-1*maxVel, maxVel);
    newSpeed = map(Vel,-1*maxVel, maxVel, -400, 400);
    return newSpeed;
}
