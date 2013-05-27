#!/usr/bin/env python

import sys
from datetime import datetime

import Tkinter
import tkMessageBox

__version__ = "1.0"


def warn(message, record=False):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showwarning('Error!', message)
    if record:
        log(message)
    sys.exit()

def error(message, record=False):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showerror('Error!', message)
    if record:
        log(message)
    sys.exit()
    
def log(message):
    with open('log.txt', 'a') as log:
        text = '\n'.join([
            'Metadata:',
            '    Timestamp: ' + str(datetime.now()),
            '    Version:   ' + __version__,
            '',
            'BEGIN MESSAGE:',
            '',
            message,
            'END MESSAGE',
            '',
            '~~~~~~~~~~~~~~~~~~~~~~',
            ''])
        log.write(text)