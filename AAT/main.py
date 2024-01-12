from container import container
from logger import log, logLevel, debug, info, warning, error, critical
import time
from utils import devBlock, isMatrix, format_list_as_table, processMatrix
import statistics
import traceback


@devBlock
def runtime():
    rt = container()
    while True:
        rt.run()


@log
def main():
    a = [[1, 2, 3], [3, 4, 4], [5, 6, 4], [7, 8, 4]]
    b = [1, 2, 3, 4, 5]
    info(a)
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
