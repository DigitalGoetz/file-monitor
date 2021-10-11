import time

with open("tempfile", "a") as thefile:
    thefile.write("LINEONE")
    time.sleep(30)
    thefile.write("LASTLINE")