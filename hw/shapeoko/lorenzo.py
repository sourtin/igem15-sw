#!/usr/bin/env python3
from .driver import Shapeoko

shap = Shapeoko("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_6493633303735140D0A0-if00")
shap.home("X", "Y", "Z")
shap.move(0, 0,20)

shap.move(0, 0 ,20)
shap.move(40, 40 ,20)
shap.move(40, 40 ,5)
shap.move(60, 60 ,5)
shap.move(60, 60 ,20)
shap.move(40, 60 ,20)
shap.move(40, 60 ,5)
shap.move(60, 40 ,5)
shap.move(60, 40 ,20)
shap.move(50, 50 ,20)

# calibrate x-axis
for x in range(0, 100):
	shap.move(150, 50 ,20)
	shap.move(48, 50 ,20)
	shap.move(48, 50 ,5)
	shap.move(52 ,50 ,5)
	shap.move(50 ,50 ,20)
# repeat like 100 times

# calibrate y-axis
for y in range(0, 100):
	shap.move(50, 150 ,20)
	shap.move(50, 48 ,20)
	shap.move(50, 48 ,5)
	shap.move(50, 52 ,5)
	shap.move(50 ,50 ,20)
# repeat like 100 times

