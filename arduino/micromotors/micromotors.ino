#include <Stepper.h>
#define NUM_MOTORS 3

const int stepsPerRevolution = 200;

int pins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

Stepper* steppers[NUM_MOTORS];

int interp = 0, motor = 0, amount = 0;

void setup() {
  Serial.begin(9600);
  for(int i=0; i < NUM_MOTORS; i+=1) {
    int n = i * 4;
    steppers[i] = new Stepper(stepsPerRevolution, pins[n], pins[n+1], pins[n+2], pins[n+3]);
    steppers[i]->setSpeed(60);
  }
}

void loop() {
  if(Serial.available() > 0) {
    char c = Serial.read();
    if(c == 'm')
      interp = 1;
    else if(c == '+')
      interp = 4;
    else if(c == '-')
      interp = 2;
    else if(c == 'g') {
      Serial.print("Going ");
      Serial.print(motor);
      Serial.print(" at ");
      Serial.println(amount);
      steppers[motor]->step((interp - 3) * amount);
      Serial.println("fin");
      Serial.flush();
      interp = 0;
      motor = 0;
      amount = 0;
    } else if(interp == 1) {
      motor = motor*10 + c - '0';
      Serial.println(motor);
    } else if(interp == 2 || interp == 4) {
      Serial.println(amount);
      amount = amount*10 + c - '0';
    }
  }
}

