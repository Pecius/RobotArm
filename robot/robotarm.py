from robot.program import ProgramError, ParserError, Program, NoneType, VariableName
from robot import ucoroutine
from robot.joint import JointRunner


class RobotArm:
	def __init__(self, joints, defaultPose):
		self.joints = joints
		self.poses = {}
		self.defaultPose = self.makepose_prep("default", defaultPose)[1]
		
		
		self.gripper = None
		self.syncMode = False
		
		instructions = {
			"rotate":		(self.rotate_cmd, [int, (int, float)], self.rotate_prep),
			"makepose":		(self.makepose_cmd, [VariableName, tuple], self.makepose_prep),
			"applypose":	(self.applypose_cmd, [VariableName]),
			"setspeed":		(self.setspeed_cmd, [(int, float), (int, float, NoneType)]),
			"syncmode":		(self.syncmode_cmd, [int]),
			"opengripper":	(self.openGripper, [int]),
			"closegripper":	(self.closeGripper, [int])#,
			#"lockjoint":	(self.lockJoint, [int]),
			#"unlockjoint":	(self.unlockJoint, [int])
		}
		
		self.program = Program(instructions)

		self.jrunner = JointRunner()

	def applyDefaultPose(self):		
		for j, v in self.defaultPose:
			j.rotate(v, True, True)
		
	def addGripper(self, gripper):
		self.gripper = gripper
		
	def closeGripper(self, x):
		self.gripper.close()
		
	def openGripper(self, x):
		self.gripper.open()
		
	def toggleGripper(self):
		self.gripper.toggle()
	
	def loadProgram(self, file):
		self.poses = {"default": self.defaultPose}
		self.syncMode = False
		self.program.parseFile(file)
		
	
	def rotate_prep(self, joint, deg):
		try:
			joint = self.joints[joint - 1]
			
			return joint, joint.calcRotation(deg)					
		
		except IndexError:
			raise ProgramError("Invalid joint number '%d'" % joint)
			
		except ValueError as e:
			raise ProgramError(e.args[0])
	
	def rotate_cmd(self, prep, joint, deg):
		if(not prep):
			joint, deg = self.rotate_prep(joint, deg)				
		
		joint.rotate(deg, False, True)
		
		self.jrunner.add(joint)
		
		return self.jrunner.run()
		
	def rotate(self, joint, deg):
		return self.rotate_cmd(False, joint, deg)

	def makepose_prep(self, name, poset):
		if(len(poset) != len(self.joints)):
			raise ProgramError("Invalid number of joints in a pose (%d should be %d)" % (len(poset), len(self.joints)))
		
		newpose = []
		
		for j, r in enumerate(poset):
			newpose.append(self.rotate_prep(j + 1, r))

		self.poses[name] = newpose
		
		return name, newpose

	def makepose_cmd(self, prep, name, poset):
		if(not prep):
			name, poset = self.makepose_prep(name, poset)
		
		self.poses[name] = poset

	def applypose_cmd(self, name):
		try:
			pose = self.poses[name]
		
		except KeyError:
			if(False and name == "default"):
				pose = self.defaultPose
			else:
				raise ProgramError("Invalid pose name '%s'" % name)
				
		jr = self.jrunner
	
		for j, p in pose:
			j.rotate(p, False, True)
			
			jr.add(j)
			
		return jr.run(self.syncMode)
		
	applyPose = applypose_cmd

	def setspeed_cmd(self, joint, speed = None):
		if(speed):
			self.joints[joint - 1].setSpeed(speed)
			return
		
		for j in self.joints:
			j.setSpeed(joint)
			
	setSpeed = setspeed_cmd
		
	def syncmode_cmd(self, enable):
		self.syncMode = bool(enable)
		
	setSyncMode = syncmode_cmd