#!/usr/bin/env python
# This file should be compatible with both Python 2 and 3.
# If it is not, please file a bug report.

"""
This is a "magic" module used to transmit the global testing flag, so modules will know if they are being tested.  (Some modules use mock objects, others don't do certain actions during testing.)
"""

#external imports
#import ...
#internal imports
#import ...

testing = False
