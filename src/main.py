from ui import AutoSweepApp
from serve import run_server
import sys


def main():
    if "--serve" in sys.argv:
        run_server()
    else:
        app = AutoSweepApp()
        app.run()


if __name__ == "__main__":
    main()
