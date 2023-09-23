#!/usr/bin/env python3


# Filter suboptimal shift key combinations.
#
# For example, Left_Shift + A and Right_Shift + Y are filtered
# to train the use of more optimal shift key combinations.
#
# NB: requires root privileges

# SPDX-FileCopyrightText: © 2023 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later


import argparse
import evdev
import signal
import sys

# FWIW: different package, higher level API we don't need here:
# import uinput


left_keys = {
        evdev.ecodes.KEY_GRAVE,
        evdev.ecodes.KEY_1,
        evdev.ecodes.KEY_2,
        evdev.ecodes.KEY_3,
        evdev.ecodes.KEY_4,
        evdev.ecodes.KEY_5,
        evdev.ecodes.KEY_Q,
        evdev.ecodes.KEY_W,
        evdev.ecodes.KEY_E,
        evdev.ecodes.KEY_R,
        evdev.ecodes.KEY_T,
        evdev.ecodes.KEY_A,
        evdev.ecodes.KEY_S,
        evdev.ecodes.KEY_D,
        evdev.ecodes.KEY_F,
        evdev.ecodes.KEY_G,
        evdev.ecodes.KEY_Z,
        evdev.ecodes.KEY_X,
        evdev.ecodes.KEY_C,
        evdev.ecodes.KEY_V,
        evdev.ecodes.KEY_B,
        }

right_keys = {
        evdev.ecodes.KEY_6,
        evdev.ecodes.KEY_7,
        evdev.ecodes.KEY_8,
        evdev.ecodes.KEY_9,
        evdev.ecodes.KEY_0,
        evdev.ecodes.KEY_MINUS,
        evdev.ecodes.KEY_EQUAL,
        evdev.ecodes.KEY_Y,
        evdev.ecodes.KEY_U,
        evdev.ecodes.KEY_I,
        evdev.ecodes.KEY_O,
        evdev.ecodes.KEY_P,
        evdev.ecodes.KEY_LEFTBRACE,
        evdev.ecodes.KEY_RIGHTBRACE,
        evdev.ecodes.KEY_BACKSLASH,
        evdev.ecodes.KEY_H,
        evdev.ecodes.KEY_J,
        evdev.ecodes.KEY_K,
        evdev.ecodes.KEY_L,
        evdev.ecodes.KEY_SEMICOLON,
        evdev.ecodes.KEY_APOSTROPHE,
        evdev.ecodes.KEY_N,
        evdev.ecodes.KEY_M,
        evdev.ecodes.KEY_COMMA,
        evdev.ecodes.KEY_DOT,
        evdev.ecodes.KEY_SLASH,
        }


def get_device_by_id(vendor, product):
    for p in evdev.list_devices():
        d = evdev.InputDevice(p)
        if len(d.capabilities().get(evdev.ecodes.EV_KEY, [])) < 100:
            continue
        if d.info.vendor == vendor and d.info.product == product:
            return p
    raise RuntimeError('could not find any device')

def get_device_by_name(name):
    for p in evdev.list_devices():
        d = evdev.InputDevice(p)
        if d.name == name:
            return p
    raise RuntimeError('could not find any device')

def parse_int(x):
    return int(x, 0)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('device', metavar='DEVICE', nargs='?',
                   help='/dev/input/eventX device to filter shift events from')
    p.add_argument('--list', '-l', action='store_true',
                   help='list keyboard devices')
    p.add_argument('--vendor', type=parse_int, help='vendor ID of device')
    p.add_argument('--product', type=parse_int, help='product ID of device')
    p.add_argument('--name', help='device name string')
    p.add_argument('--systemd', '-D', action='store_true',
                   help='notify systemd when running as a service')
    args = p.parse_args()
    if not (args.list or args.device or args.vendor is not None or args.product is not None or args.name):
        raise RuntimeError('Either specify --list or --vendor/--product ID or a DEVICE')
    if args.vendor is not None or args.product is not None:
        if args.vendor is None or args.product is None:
            raise RuntimeError('Specify both --vendor and --product')
        args.device = get_device_by_id(args.vendor, args.product)
    if args.name:
        args.device = get_device_by_name(args.name)
    return args

def list_devices():
    print(f'{"device":<20} {"vendor":>7} {"product":>7}   name')
    for p in evdev.list_devices():
        d = evdev.InputDevice(p)
        if len(d.capabilities().get(evdev.ecodes.EV_KEY, [])) < 100:
            continue
        print(f'{d.path:<20} {d.info.vendor:>#7x} {d.info.product:>#7x}   {d.name}')


def transcribe(d):
    with evdev.UInput.from_device(d, name='virtual-keyboard') as u, d.grab_context():
        lshift_pressed = False
        rshift_pressed = False
        for e in d.read_loop():
            if e.type != evdev.ecodes.EV_KEY:
                continue

            if   e.code == evdev.ecodes.KEY_LEFTSHIFT:
                lshift_pressed = e.value != 0
            elif e.code == evdev.ecodes.KEY_RIGHTSHIFT:
                rshift_pressed = e.value != 0

            if  lshift_pressed and e.code in left_keys:
                continue
            if rshift_pressed  and e.code in right_keys:
                continue

            u.write_event(e)
            u.syn()

def mainP():
    args = parse_args()
    if args.list:
        return list_devices()

    d = evdev.InputDevice(args.device)

    if args.systemd:
        import systemd.daemon
        systemd.daemon.notify('READY=1')

    return transcribe(d)


def on_sigterm(sig, frm):
    # raise this as we already deal with it ...
    raise KeyboardInterrupt()

def main():
    try:
        signal.signal(signal.SIGTERM, on_sigterm)
        return mainP()
    except KeyboardInterrupt:
        pass
    # except Exception as e:
    #     print(f'Error: {e}', file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main())


