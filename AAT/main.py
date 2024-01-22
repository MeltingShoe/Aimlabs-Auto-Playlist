

import time
from utils import devBlock
import traceback
from modelLoader import loadModel
from readDB import readAimlabsDB
from logger import log, logLevel, debug, info, warning, error, critical


@devBlock
def runtime():
    db = readAimlabsDB()
    rt = loadModel()
    while True:
        rt.run(db)


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
