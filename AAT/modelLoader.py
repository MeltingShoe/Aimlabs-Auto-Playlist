from logger import log, logLevel, debug, info, warning, error, critical
import pickle
import os
from container import container
from readDB import readAimlabsDB

savePath = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, 'savedModelState.pkl'))


@log
def checkSave():
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
        with open(savePath, 'wb') as pickle_file:
            pickle.dump(runtime, pickle_file)
    return runtime
