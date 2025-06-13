#!/usr/bin/env python
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the app from application.py
from application import app as application

if __name__ == '__main__':
    application.run()
