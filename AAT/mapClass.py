from logger import log, logLevel, debug, info, warning, error, critical
from utils import launchTask
from functionGenerator import func
from convolution import convolution
from maxStepFunc import step


class aatMap:
    def __init__(self, mapData):
        self.DBname = mapData['name']
        self.ID = mapData['ID']
        tn = mapData['taskName']
        s = mapData['size']
        d = mapData['difficulty']
        # this looks confusing and stupid but it's just formatting a string don't pay attention to it I need to learn to do this properly
        self.displayName = 'AAT ' + tn + ' ' + s + 'R ' + d
        self.x = mapData['x']
        self.y = mapData['y']
        self.lockVal = mapData['lockVal'] if mapData['lockVal'] is not None else 0
        # just setting these to defaults is values aren't set
        scores = mapData['scores']
        self.scores = scores if scores is not None else []
        self.weightFunc = mapData['weightFunc']
        # you're expected to pass the function in it's entirety
        self.performanceFunction = mapData['performanceFunction']
        # have to pass an objects method so all the maps can use the same function and the number of runs will update correctly
        self.getStepLen = mapData['getStepLen']
        # wow we sure love passing functions dont we
        self.conv = mapData['convolutionFunction']

    @log
    def checkScore(self, taskData):
        out = {'isValid': False, 'taskData': taskData}
        if score['name'] != self.DBname:
            return out
        out['isValid'] = True
        out['x'] = self.x
        out['y'] = self.y
        # Doing all the calculation of performance and the length of step to take here
        out['performance'] = self.performanceFunction(out['score'])
        base = self.lockVal
        step = out['performance'] - base
        out['step'] = self.getStepLen(step)
        return out

    @log
    def updateWeight(self, step, origin):
        data = {'step': step, 'x': self.x, 'y': self.y}
        adjustment = self.conv(data, origin)
        self.lockVal += adjustment
        out = {'lockVal': self.lockVal, 'weight': self.getWeight(),
               'adjustment': adjustment}
        return out

    @log
    def launchMap(self):
        launchTask(self.ID)
        return True

    @log
    def getWeight(self):
        return self.weightFunc(self.lockVal)

    @log
    def mapSelection(self, key):
        # we're moving the functionality of making a random selection into the maps
        # basically we pick a key and then iterate through each map subtracting their weight from the key. once the key is below 0 we've made our selection
        # if we do pick this map we return the method to launch the map directly
        weight = self.getWeight()
        key = key - weight
        out = {'mapSelected': key <= 0, 'key': key}
        if out['mapSelected']:
            out['runMap'] = self.launchMap
            out['processScore'] = self.checkScore
        return out


class mapFactory:
    def __init__(self, taskSetData):
        self.conv = convolution(taskaSetData['convolutionFunction'])
        self.performanceFunction = func(taskSetData['performanceFunction'])
        self.maxStep = stepFunction(taskSetData['stepFunc'])
        self.weightFunc = func(taskSetData['weightFunc'])
        self.taskName = taskSetData['taskSetName']

    def __call__(self, mapData):
        return self.createMap(mapData)

    def createMap(self, mapData):
        mapData['taskName'] = self.taskName
        mapData['convolutionFunction'] = self.conv
        mapData['getStepLen'] = self.maxStep
        mapData['performanceFunction'] = self.performanceFunction
        mapData['weightFunc'] = self.weightFunc
        mapObject = aatMap(mapData)
        return mapObject
