from container import container
from logger import log, logLevel, debug, info, warning, error, critical
import time
from utils import devBlock
import statistics
import traceback


@devBlock
def runtime():
    rt = container()
    while True:
        rt.run()


@log
def main():
    try:
        runtime()
    except KeyboardInterrupt:
        # Log the keyboard interrupt as critical
        critical("Keyboard interrupt received.")
    except Exception as e:
        stack_trace = traceback.format_exc()
        critical(f"Unhandled exception: {str(e)}\n{stack_trace}")


if __name__ == '__main__':
    main()
    time.sleep(1)
