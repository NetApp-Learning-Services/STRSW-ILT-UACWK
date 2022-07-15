#!/usr/bin/env python

"""
Example solution for Exercise 6, Task 3, Step 3-23

"""

import sys
import time
import astraSDK

appID = 'change_me'
name = 'change_me'

def doSnapshot(appID, name):
    protectionID = astraSDK.takeSnap().main(appID, name)
    if protectionID == False:
        sys.exit(1)

    print(f"Starting snapshot of {appID}")
    print(f"Waiting for snapshot to complete.", end="")
    sys.stdout.flush()
    while True:
        objects = astraSDK.getSnaps().main()
        if not objects:
            print(f"Taking snapshot failed")
            return False
        for obj in objects["items"]:
            if obj["id"] == protectionID:
                if obj["state"] == "completed":
                    print("complete!")
                    sys.stdout.flush()
                    return protectionID
                elif obj["state"] == "failed":
                    print(f"Snapshot job failed")
                    return False
        time.sleep(5)
        print(".", end="")
        sys.stdout.flush()

if __name__ == "__main__":
    rc = doSnapshot(appID, name)
    if rc is False:
        print("doSnapshot failed")
        sys.exit(1)
    else:
        sys.exit(0)
