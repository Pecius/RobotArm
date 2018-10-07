from robot import ucoroutine
from machine import PWM

from robot.servo import Servo, CalibrationData
from robot.joint import ServoJoint, JointGroup

servo1PWM = PWM(26, freq = 50, resolution = 13)

servo1Cal	= CalibrationData(187, 1053, 233, 1041, 182)
servo1		= Servo(servo1PWM, servo1Cal)
servo1Joint	= ServoJoint(servo1)


servo4PWM	= PWM(25, freq = 50, resolution = 13)

servo4Cal	= CalibrationData(186, 1054, 250, 1043, 182)
servo4		= Servo(servo4PWM, servo4Cal)
servo4Joint	= ServoJoint(servo4)



#servo3PWM	= PWM(27)
#servo3PWM.freq(50, 13)

#servo3Cal	= CalibrationData(186, 1050, 244, 1027, 182, 180, 192)
#servo3		= Servo(servo3PWM, servo3Cal)
#servo3Joint	= ServoJoint(servo3, False, -145, 50, 145)

servo5PWM	= PWM(14, freq = 50, resolution = 13)

servo5Cal	= CalibrationData(185, 1044, 229, 1013, 182, 180, 192)
servo5		= Servo(servo5PWM, servo5Cal)
servo5Joint	= ServoJoint(servo5, True, -90, 90, 98.5 + 5)

servo2PWM	= PWM(27, freq = 50, resolution = 13)

servo2Cal	= CalibrationData(186, 1048, 204, 994, 182)
servo2		= Servo(servo2PWM, servo2Cal)
servo2Joint	= ServoJoint(servo2, False, -145, 50, 145 + 15)


servo0PWM	= PWM(33, freq = 50, resolution = 13)

servo0Cal	= CalibrationData(192, 1076, 240, 1028, 180)
servo0		= Servo(servo0PWM, servo0Cal)
servo0Joint	= ServoJoint(servo0, True, -90, 90, 81)

servo6PWM	= PWM(12, freq = 50, resolution = 13)

servo6Cal	= CalibrationData(185, 1046, 255, 1033, 182)
servo6		= Servo(servo6PWM, servo6Cal)
servo6Joint	= ServoJoint(servo6, True, -90, 90, 90)

RoboJoint1 = servo0Joint
RoboJoint2 = JointGroup(servo1Joint, servo4Joint)
RoboJoint3 = servo2Joint
RoboJoint4 = servo5Joint
RoboJoint5 = servo6Joint

joints = [RoboJoint1, RoboJoint2, RoboJoint3, RoboJoint4, RoboJoint5]


from _thread import start_new_thread



from robot.simplegripper import SimpleGripper
from robot.robotarm import RobotArm

ra = None

def main():
	global ra
	ra = RobotArm(joints, (0, 180-45, -130, 0, 0))

	ra.addGripper(SimpleGripper(PWM(13, freq=50, resolution=13), 601, 409))
	ra.applyDefaultPose()

	co = ucoroutine.uCoroutine(1)
	co.add(ra.program.run())
	
	co.run()
