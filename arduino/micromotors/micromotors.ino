// Combined motor control and led control board
// ~ moosd 2015

// install accelstepper from http://www.airspayce.com/mikem/arduino/AccelStepper
#include <AccelStepper.h>

// Configuration for pinouts
const int motor_pins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
const int led_pins[] = {A0, A1, A2};

// Initalise variables related to stepper control and state
#define NUM_MOTORS ((sizeof(motor_pins)/sizeof(*motor_pins))/4)
AccelStepper* steppers[NUM_MOTORS];
int stepper_states[NUM_MOTORS];

// Initalise variables related to led control
#define NUM_LEDS (sizeof(led_pins)/sizeof(*led_pins))

// Initalise variables related to command interpreter
int interp = 0, motor = 0, amount = 0, led = 0, bright = 255;

void setup() {
  Serial.begin(9600);
  // Initialise motors by parsing motor_pins in blocks of four.
  for(int i=0; i < NUM_MOTORS; i+=1) {
    int n = i * 4;
    steppers[i] = new AccelStepper(AccelStepper::FULL4WIRE, motor_pins[n], motor_pins[n+1], motor_pins[n+2], motor_pins[n+3]);
    steppers[i]->setMaxSpeed(600.0);
    steppers[i]->setAcceleration(300.0);
    stepper_states[i] = 0;
  }
  // Initialise led outputs
  for(int i = 0; i < NUM_LEDS; i++)
    pinMode(led_pins[i], OUTPUT);
  // turn on and say that we're ready
  activateLeds();
  Serial.println("micromotors connected.");
  Serial.flush();
}

void activateLeds() {
  for(int i = 0; i < NUM_LEDS; i++)
    analogWrite(led_pins[i], 0);
  analogWrite(led_pins[led], bright);
}

void loop() {
  // Perform movement of motors
  for(int i=0; i < NUM_MOTORS; i+=1) {
    if(stepper_states[i] == 1) {
      if (steppers[i]->distanceToGo() == 0) {
        stepper_states[i] = 0;
        steppers[i]->disableOutputs();
      } else steppers[i]->run();
    }
  }

  // Command interpreter code
  // a = get led that is on
  // c = get brightness
  // mX<+/->Yg = make motor X go <clockwise|anticlockwise> Y steps
  // lXb = turn led X on
  // +Xd =  set brightness to X - ONLY WORKS ON PINS 3, 5, 6, 9, 10, and 11.
  if(Serial.available() > 0) {
    char c = Serial.read();

    // LED commands
    if(c == 'l') {
      interp = 5;
      led = 0;
    } else if(c == 'd') {
      bright = amount % 256;
      amount = 0;
      interp = 0;
      activateLeds();
    } else if(c == 'b') {
      // Activate the right leds
      led = led % NUM_LEDS;
      activateLeds();
      amount = 0;
      interp = 0;
    } else if(c == 'a') {
      Serial.write(led);
      Serial.flush();
    } else if(c == 'c') {
      Serial.write(bright);
      Serial.flush();
    }
    // Motor commands
    else if(c == 'm')
      interp = 1;
    else if(c == '+')
      interp = 4;
    else if(c == '-')
      interp = 2;
    else if(c == 'g') {
      // Activate motors
      motor = motor % NUM_MOTORS;

      if(stepper_states[motor] == 0) {
          stepper_states[motor] = 1;
          steppers[motor]->enableOutputs();
      }
      steppers[motor]->move((interp - 3) * amount);

      interp = 0;
      motor = 0;
      amount = 0;
    } else if(interp == 1)
      motor = motor*10 + c - '0';
    else if(interp == 2 || interp == 4)
      amount = amount*10 + c - '0';
    else if(interp == 5)
      led = led*10 + c - '0';
  }
}

