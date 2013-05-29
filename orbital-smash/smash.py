#!/usr/bin/env python
'''
Orbital-smash

A game written in twenty-four hours.
'''

import sys
import errors
import traceback
import frames

__version__ = errors.__version__
__release__ = errors.__release__


def main():
    '''
    The main, top-level function and starting point of the game.

    Also catches any errors that may occur, and cleanly logs and reports them.
    '''
    try:
        frames.mainloop()
    except SystemExit:
        pass
    except Exception:
        error = traceback.format_exc()
        errors.log('Top-level exception: ' + error)
        if '--debug' in sys.argv:
            print error
        else:
            errors.error('The program encountered an unexpected error.\n\n' + 
                'Please see "log.txt" for details, and send an email to ' +
                '"michael.lee.0x2a@gmail.com" for help.')

if __name__ == '__main__':
    main()
