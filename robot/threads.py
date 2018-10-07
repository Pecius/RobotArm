from _thread import start_new_thread

from robot import input
from robot import ui
from robot import st

RA		= start_new_thread("RobotArm", st.main, (), None, True, 1024*7)
Input	= start_new_thread("Input", input.main, (), None, False, 1024*7)
UI		= start_new_thread("UI", ui.main, (), None, True, 1024*9)
