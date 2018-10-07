import ure
from micropython import const
from robot import ucoroutine
from array import array
from gc import collect as gccollect

issubclass = issubclass
isinstance = isinstance

len = len

FunctionType	= type(lambda x: x)
GeneratorType	= type((lambda: (yield))())

NoneType		= type(None)
CompileType		= type(compile("1", "", "eval"))

_stringstart = ure.compile("^\s*\"(.*)")
_stringend = ure.compile("(.*)\"\s*$")
_fullstring = ure.compile("^\s*\"(.*)\"\s*$")
_number = ure.compile("^\s*(\-?\d+\.?\d*)\s*$")
_var = ure.compile("^\s*([a-zA-Z_][a-zA-Z0-9_]+)\s*$")

_varM = ure.compile("\s*([a-zA-Z_][a-zA-Z0-9_]+)\s*")
_function = ure.compile("([a-zA-Z_][a-zA-Z0-9_]+)\s*\(")
_operations = ure.compile("[/\+\*=\(\)<>\-]")

_PROGRAM_STATE_STOP		= const(0)
_PROGRAM_STATE_RUN		= const(1)
_PROGRAM_STATE_PAUSE	= const(2)
_PROGRAM_STATE_ERROR	= const(3)

class ProgramError(Exception):
	def __str__(self):
		return b"Program error, line %d: %s" % (self.args[0], self.args[1])
	
class ParserError(Exception):
	def __str__(self):	
		return b"Parser error, line %d: %s" % (self.args[0], self.args[1])

class VariableName:
	pass

class Variable:
	def __init__(self, name):
		self.name = name
		
	def __str__(self):
		return "<Program variable> '%s'" % self.name
		
def __makeTypeErrorMsg(got, expected):
	got = got.__name__
	
	if(type(expected) == tuple):
		names = []
		for t in expected:
			names.append(t.__name__)
			
		expected = " or ".join(names)
		
	else:
		expected = expected.__name__
		
	return "Invalid type. Expected %s got %s" % (expected, got)
		
def __parse_args(args, str):
	dynamic = False
	stringbuff = None
	p = str.split(";")
	
	for s in p:
		if(stringbuff):
			r = _stringend.match(s)
			if(r):
				stringbuff.append(";" + r.group(1))
				args.append("".join(stringbuff))
				
				stringbuff = None
			else:
				stringbuff.append(";" + s)
				
			continue
		
		if(len(s) == 0):
			args.append(None)
			continue
		
		r = _fullstring.match(s)
		
		if(r):
			args.append(r.group(1))
			continue
			
		r = _stringstart.match(s)
		
		if(r):
			stringbuff = [r.group(1)]	
			continue
		
		r = _number.match(s)
		
		if(r):
			n = r.group(1)
			try:
				v = int(n)
			except:
				v = float(n)
				
			args.append(v)
			continue
		
		r = _var.match(s)
		
		if(r):
			dynamic = True
			args.append(Variable(r.group(1)))
			continue
		
		r = _operations.search(s)
		
		if(r):
			try:
				if(_varM.search(s)):
					v = compile(s.strip(), "", "eval")
					dynamic = True
				else:
					v = eval(s.strip())
					
				args.append(v)
				continue
			except Exception as e:
				raise ParserError(*e.args)
		
		raise ParserError("Invalid argument format '%s'" % s)
		
		
	return dynamic

def __check_types(values, types):
	lv = len(values)

	if(len(types) < lv):
		raise ParserError("Too many arguments")

	for i in range(len(types)):
		t = types[i]
		v = type(values[i]) if i < lv else NoneType
		
		if(not issubclass(v, t) and (not issubclass(v, Variable) and not issubclass(v, CompileType))):
			raise ParserError(__makeTypeErrorMsg(v, t))
	
class Program:
	__instrRE = ure.compile("\s*(\S+)\s+(.+)")
	__labelRE = ure.compile("\s*(\S+):\s*")
	
	
	STOPPED	= _PROGRAM_STATE_STOP
	RUNNING	= _PROGRAM_STATE_RUN
	PAUSED	= _PROGRAM_STATE_PAUSE
	ERROR	= _PROGRAM_STATE_ERROR
	
	def __init__(self, instructionSet, builtinSet = None):
		self.program = []
		self.labels = {}
		self.variables = {}
		self.globals = {}
		self.constants = {}
		self.lines = array(b"H")
		
		self.instructionSet = instructionSet
		
		if(builtinSet is None):
			builtinSet = {
				"wait": (self.wait, ((int, float),)),
				"goto": (self.goto, (int,)),
				"setvar": (self.setVar, (VariableName, (int, float, str))),
				"gotoif": (self.gotoIf, (int, (int, float, bool)))
			}
		
		self.builtinSet = builtinSet
		
		self.curLine = 0
		self.parsedLine = 1
		
		self.programFile = None
		self.currentFile = None

		self.programState = _PROGRAM_STATE_STOP
		self.lastError = None
	
	def clear(self):
		self.stop()
	
		self.program = []
		self.labels = {}
		self.variables = {}
		self.globals = {}
		self.constants = {}
		self.lines = array(b"H")
		
		self.parsedLine = 1
		self.programFile = None
		self.currentFile = None
		self.lastError = None
	
	def parseFile(self, file):
		self.clear()
		gccollect()
	
		with open(file, "r") as f:
			for l in f:
				self.parseLine(l)
			
			self.programFile = file
			
		self.resolveConstants()
	
	def parseLine(self, str):
		str = str.partition("#")[0]
		
		if(len(str) == 0 or str.isspace()):
			self.parsedLine += 1
			return
		
		match = self.__labelRE.match(str)
		
		if(match):
			label = match.group(1)
			self.globals[label] = len(self.program)
			self.constants[label] = len(self.program)
			
			self.parsedLine += 1
			return
		else:
			match = self.__instrRE.match(str)
			if(not match):
				raise ParserError(self.parsedLine, "Invalid instruction syntax '%s'" % str)
			
		
		instruction = match.group(1).lower()
	
		inst = self.instructionSet.get(instruction) or self.builtinSet.get(instruction)
		
		if(not inst):
			raise ParserError(self.parsedLine, "Invalid instruction '%s'" % instruction)
		
		args = []
		
		
		try:
			dynamic = __parse_args(args, match.group(2))
		except ParserError as e:
			raise ParserError(self.parsedLine, *e.args)
		

		try:
			__check_types(args, inst[1])
		except ParserError as e:
			raise ParserError(self.parsedLine, *e.args)
		
		
		if(len(inst) == 3):
			if(not dynamic):
				try:
					res = inst[2](*args)
					
					args = [True]
					args.extend(res)
	
				except ProgramError as e:
					raise ParserError(self.parsedLine, *e.args)
			else:
				args.insert(0, False)


		self.program.append((inst, args, dynamic))
		self.lines.append(self.parsedLine)
		self.parsedLine += 1
	

	def gotoIf(self, pos, value):
		if(value == True):
			self.goto(pos)
	
	def setVar(self, name, value):		
		if(name in self.globals):
			raise ProgramError(self.currentLine(), "Trying to override a global variable '%s'" % name)
		
		self.variables[name] = value
	
	def goto(self, line):
		if(line < 0):
			raise ProgramError(self.currentLine(), "Invalid goto value of '%s'" % line)
	
		self.curLine = line - 1

	async def wait(self, time):
		yield time * 1000
	
	def stop(self, error = False):
		self.programState = _PROGRAM_STATE_ERROR if error else _PROGRAM_STATE_STOP
		self.curLine = 0
		
	def pause(self):
		self.programState = _PROGRAM_STATE_PAUSE
		
	def start(self):
		self.lastError = None
		self.programState = _PROGRAM_STATE_RUN
		
	def currentLine(self):
		try:
			return self.lines[self.curLine]
		except IndexError:
			return 0
			
	def resolveConstants(self):
		for p, line in enumerate(self.program):
			if(line[2]):
				hasprep = len(line[0]) == 3
				
				bpos = 1 if hasprep else 0
				args = line[1]
				dynamic = False
				
				for k in range(bpos, len(args)):
					v = args[k]
					
					if(isinstance(v, Variable)):
						if(issubclass(VariableName, line[0][1][k - bpos])):
							args[k] = v.name
						elif(v.name in self.constants):
							args[k] = self.constants[v.name]
						else:
							dynamic = True
							
					elif(isinstance(v, CompileType)):
						dynamic = True
						
						
				if(not dynamic):
					if(hasprep):
						try:
							del args[0]
							res = line[0][2](*args)
							
							args = [True]
							args.extend(res)
			
						except ProgramError as e:
							raise ParserError(self.lines[p], *e.args)
				
					self.program[p] = (line[0], args, False)
				
				
		self.constants = {}
	
	async def run(self):
		while(True):
			while(self.programState != _PROGRAM_STATE_RUN):
				yield 100
				
			try:
				t = self.program[self.curLine]
			except IndexError:
				self.stop()

				continue
			
			try:
				inst = t[0]
				args = t[1]
				
				if(t[2]):
					if(len(inst) == 3):
						bpos = 1
						nargs = [False]
					else:
						bpos = 0
						nargs = []
						
					types = inst[1]
					
					for k in range(bpos, len(args)):
						v = args[k]
						res = None

						if(isinstance(v, Variable)):
							if(issubclass(VariableName, types[k - bpos])):
								continue
							else:
								res = self.variables.get(v.name)
								
								if(res is None):
									res = self.globals.get(v.name)
								
						elif(isinstance(v, CompileType)):
							res = eval(v, self.globals, self.variables)
						else:
							nargs.append(v)
							continue
						
						if(not isinstance(res, types[k - bpos])):
							raise ProgramError(__makeTypeErrorMsg(type(res), types[k - bpos]))
						

						nargs.append(res)
						
					args = nargs
			
				r = inst[0](*args)
				
				if(isinstance(r, GeneratorType)):	
					await r
				
			except ProgramError as ex:
				ex = ProgramError(self.currentLine(), *ex.args)
				
				print("Error while executing program", ex)
				
				self.lastError = ex
				self.stop(True)
				continue
				
			self.curLine += 1
