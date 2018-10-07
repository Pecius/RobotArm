import machine

encoderAPin		= 35 #DT
encoderBPin		= 34 #CLK
encoderButton	= machine.Pin(32)

# I2C

i2c = machine.I2C(scl = 2, sda = 15)

keypadAddress	= 32
displayAddress	= 39
