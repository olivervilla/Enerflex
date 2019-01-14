import os
import sys

restart = str(raw_input("\nDo you want to restart the program? [y/n] > "))

if restart == "y":
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
else:
    print("\nThe programm will me closed...")
    sys.exit(0)
