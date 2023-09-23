This repository contains shift-tutor, a small Python script that filters
suboptimal shift key combinations, on Linux.

That way it helps to train muscle memory for using both
shift keys when touch typing.

It might also serve as a concise example of how keyboard events
can be easily read, filtered, manipulated and injected on Linux.

2023, Georg Sauthoff


## Usage

On Fedora, install dependencies:

    dnf install python3-evdev

List all available keyboards:

    shift-tutor.py -l

Actively filter a certain keyboard:

    shift-tutor.py /dev/...

Or by name:

    shift-tutor.py --name 'Some Keyboard Name'

Note that the script requires root privileges.


## How it works

It uses the Linux [evdev][1] API to exclusively grab a keyboard and
inject a subset of the arriving keycodes  back to the system,
using the Linux [uinput API][2], via a virtual keyboard.

For accessing these APIs from Python, shift-tutor uses the fine
[python-evdev][3] package.


[1]: https://en.wikipedia.org/wiki/Evdev
[2]: https://kernel.org/doc/html/latest/input/uinput.html
[3]: https://github.com/gvalkov/python-evdev
