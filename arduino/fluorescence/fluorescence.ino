int outpins[] = {12, 13};
int last = 0, mode = 1, outsz = (sizeof(outpins)/sizeof(*outpins));

void setup() {
  pinMode(11, INPUT);
  for(int i = 0; i < outsz; i++)
    pinMode(outpins[i], OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int val = digitalRead(11);
  if(val != last && val) mode=(mode+1)%outsz;
  last = val;
  delay(100);

  if(Serial.available()) {
    mode=(Serial.read())%outsz;
  }

  for(int i = 0; i < outsz; i++)
    digitalWrite(outpins[i], LOW);
  digitalWrite(outpins[mode], HIGH);
}
