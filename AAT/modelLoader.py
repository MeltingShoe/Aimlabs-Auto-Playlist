from logger import log, logLevel, debug, info, warning, error, critical, logger_instance
import pickle
import os
from container import container
from readDB import readAimlabsDB
from utils import openYAML
config = openYAML('devConfig.yaml')
savePath = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, config['savePath']))

loadEnable = config['loadEnable']


@log
def checkSave():
    if not loadEnable:
        return False
    return os.path.isfile(savePath)


@log
def loadModel():
    if checkSave():
        info('Loading saved model data')
        with open(savePath, 'rb') as pickle_file:
            runtime = pickle.load(pickle_file)
    else:
        warning('NO SAVED DATA FOUND')
        db = readAimlabsDB()
        runtime = container(db)
        # logger_instance.acc.start()
        with open(savePath, 'wb') as pickle_file:
            pickle.dump(runtime, pickle_file)
        # logger_instance.acc.stop()
    return runtime
