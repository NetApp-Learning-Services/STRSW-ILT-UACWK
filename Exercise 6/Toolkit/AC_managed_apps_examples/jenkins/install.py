#!/usr/bin/env python
"""Wrapper script around toolkit.py deploy chart appname namespace"""

import argparse
import os
from shutil import which
import sys

myPath = os.path.realpath(sys.argv[0])
# The name of the directory we are in will be the name of the chart deployed
appName = os.path.split(os.path.dirname(myPath))[1]
# toolkitPath is None if toolkit.py is not in PATH
toolkitPath = which("toolkit.py")

testPath = myPath
while not toolkitPath:
    # Look for toolkit.py in the subtree we are in
    if os.path.isfile(os.path.join(testPath, "toolkit.py")):
        toolkitPath = os.path.join(testPath, "toolkit.py")
        break
    if testPath == "/":
        # toolkit.py wasn't found
        print("toolkit.py not found")
        sys.exit(1)
    # Try the directory above next
    testPath = os.path.split(testPath)[0]

if not os.access(toolkitPath, os.X_OK):
    print("toolkit.py found at %s, but not executable") % toolkitPath
    sys.exit(2)

parser = argparse.ArgumentParser()
parser.add_argument(
    "app",
    help="name of app",
)
parser.add_argument(
    "namespace", help="Namespace to deploy into (must not already exist)"
)
args = parser.parse_args()
ret = os.system(
    """ "%s" deploy %s %s %s""" % (toolkitPath, appName, args.app, args.namespace)
)
# python is inverted from shell return codes
if ret:
    print("Deployment failed!")
    sys.exit(1)
else:
    sys.exit(0)
