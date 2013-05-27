#!/usr/bin/env python

import errors
import traceback
import frames

if __name__ == '__main__':
    try:
        frames.mainloop()
    except Exception as err:
        error = traceback.format_exc()
        errors.log('Top-level exception: ' + error)
        errors.error('The program encountered an unexpected error.\n\n' + 
            'Please see "log.txt" for details, and send an email to ' +
            '"michael.lee.0x2a@gmail.com" for help.')

    