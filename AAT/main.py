from container import container
from logger import log, logLevel, debug, info, warning, error, critical
import time


@log
def main():
    try:
        rt = container()
        while True:
            rt.run()
    except KeyboardInterrupt:
        # Log the keyboard interrupt as critical
        critical("Keyboard interrupt received.")
    except Exception as e:
        # Log other exceptions as critical
        critical(f"Unhandled exception: {str(e)}")


if __name__ == '__main__':
    main()
    time.sleep(3)
