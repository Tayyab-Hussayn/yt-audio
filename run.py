#!/usr/bin/env python3

import sys
import os
import runpy

# Add the project's root directory to the Python path, not just 'src'
# This helps Python understand the project structure.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Use runpy to execute the 'main' module from the 'src' package
# This correctly handles relative imports within the 'src' package.
runpy.run_module('src.main', run_name='__main__')

