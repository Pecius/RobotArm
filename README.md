This was a part of my engineering project.

The project is dedicated for ESP32 SoC with MicroPython firmware based on [Loboris' implementation](https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo).

# Features

## User interface
The UI is based on an alphanumeric display controlled with an encoder and a 4x4 membrane keypad.
The core of UI has been written as a separate module which does not depend on a specific implementation of input devices or a display. However, it's developed with alphanumeric displays in mind. It's easily extensible due to its class based implementation.
Currently at its core it implements basic elements such as:
- Buttons
- Checkboxes
- Numeric/text entry
- Scrollable menu
  - File selection
- Static text
  - Scrollable multi-line text

Robot's UI consists of:
- Program screen
  - Displays currently executed instruction as well as previous and next one
  - Displays program execution status (running, paused, stopped)
- Program selection
- Manual joint control
- Configuration menu
  - Wi-Fi configuration (enable, SSID, password)
  - FTP/telnet (enable, login, password)

Text is inputted using a keypad and a multi-tap interface (like it used to be in old cellphones).

## Programming
The robot is programmable using a simple command based language. The language supports label based conditional jumps, variables, external variables and basic arithmetic operations.
The inputted program is parsed into a tuple that contains a method that represents the instruction and processed arguments.
The instruction arguments are optimized if they're constant (eg. expression "2 + 2" is turned into its result value of 4) and then further processed if the instruction implements a preparation method (for example *rotate* instruction turns degrees directly into a servo pulse width in this stage).


## Miscellaneous
The software is running on a mix of threads and simplified coroutine system spanning over both cores of ESP32.
The keypad is interfaced using I2C communication protocol. Additionally, this implementation is capable of reading multiple key presses at once.