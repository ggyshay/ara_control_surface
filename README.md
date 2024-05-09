# ARA Surface Controler

## Controller Structure

Controllers in this project have a `surfaceControl` as the root. You can find the implementation details in the `ARA.py` file.

### Control Surface Elements

Control Surface Elements are used to represent things like buttons, knobs, sliders, etc. They provide the basic building blocks for creating the controller's user interface.

### Control Surface Components

Control Surface Components are used to represent functionality or behavior of the controller. They encapsulate a set of related control surface elements and define how they interact with the software.

## useful stuff

### Tail abletons logs with

`C:\Documents and Settings\<user>\Application Data\Ableton\Live 9.1\Preferences\`
on windows or

`/Users/<user>/Library/Preferences/Ableton/Live 9.1/`
on mac and execute
`tail -f Log.txt`
