from functionGenerator import func
from utils import saveYAML, openYAML, launchTask, scoreDB, rawDB
from logger import log, logLevel, debug, info, warning, error, critical
from convolution import convolution
import random
import numpy


class taskSet:
    def __init__(self, configPath):
        self.debug = True
        self.runs = 0
        self.config = openYAML(configPath)
        self.conv = convolution(self.config['convConfigFileName'])
        self.BMs = self.config['benchmarks']
        self.trainers = self.config['trainers']
        self.runsSinceBM = -3
        self.maxIntervalBM = self.config['maxIntervalBM']
        self.decayBM = func(self.config['decayBM'])
        self.scoreFunc = self.config['scoreFunc']
        self.performanceFunction = func(self.config['performanceFunction'])
        self.stats = {}
        self.lastBM = False
        nameList = self.getNameList()
        mainConfig = openYAML('config.yaml')
        self.db = scoreDB(nameList, resetPoint=mainConfig['resetPoint'])
        self.stepFunc = func(self.config['stepFunc'])
        self.weightFunc = func(self.config['weightFunc'])
        self.processNewScores()

    @log
    def runTask(self):
        task = self.getTask()
        ID = task['ID']
        tName = self.config['taskSetName'] + ' ' + \
            task['size'] + 'R ' + task['difficulty'] + 'T'
        running = True
        while running:
            print('Launching '+tName)
            launchTask(ID)
            print('type YES when done')
            inv = input()
            if inv != 'YES':
                continue
            return self.processNewScores()

    @log
    def getTask(self):
        runBM = self.trainOrBM()
        self.lastBM = runBM
        if runBM:
            self.runsSinceBM = 0
            return self.getBMTask()
        else:
            self.runsSinceBM += 1
            return self.getTrainingTask()

    @log
    def trainOrBM(self):
        if self.runsSinceBM == -1:
            self.runsSinceBM += 1
            return True
        x = self.runsSinceBM / self.maxIntervalBM
        w = self.decayBM.getOutput(x)
        point = random.randint(0, 1000000)/1000000
        return point < w

    @log
    def getBMTask(self):
        index = random.randint(0, (len(self.BMs)-1))
        return self.BMs[index]

    @log
    def getTrainingTask(self):
        x, y = self.selectTraining()
        return self.trainers[y][x]

    @log
    def selectTraining(self):
        wMatrix = self.getWeights()
        total = 0
        for row in wMatrix:
            for item in row:
                total += item
        key = random.uniform(0, total)
        x = 0
        y = 0
        for row in wMatrix:
            x = 0
            for item in row:
                if key < item:
                    return x, y
                key -= item
                x += 1
            y += 1
        raise Exception('selection failed somehow')

    @log
    def getWeights(self):
        out = []
        for row in self.trainers:
            line = []
            for item in row:
                val = abs(item['lockVal'])
                w = self.weightFunc(val)
                line.append(w)
            out.append(line)
        return out

    @log
    def processNewScores(self):
        while True:
            score = self.db()
            if score == False:
                break
            else:
                self.processScore(score)

    @log
    def processScore(self, score):
        score = self.processScoreXY(score)
        convOut = self.processResults(score, score['x'], score['y'])
        self.runs += 1
        return convOut

    @log
    def processScoreXY(self, score):
        for task in self.BMs:
            if score['name'] == task['name']:
                score['x'] = task['x']
                score['y'] = task['y']
                return score
        for row in self.trainers:
            for task in row:
                if score['name'] == task['name']:
                    score['x'] = task['x']
                    score['y'] = task['y']
                    return score

    @log
    def processResults(self, taskData, x, y):
        if y == -1:
            return self.processBM(taskData, x)
        score = self.parseScore(taskData)
        convOut = self.convolve(x, y, score)
        return convOut

    @log
    def processBM(self, taskData, x):
        self.BMs[x]['score'] = taskData['score']

    @log
    def parseScore(self, taskData):
        if self.scoreFunc == '1W6TPOP':
            return self.score1w6tPOP(taskData)
        raise Exception('invalid score function')

    @log
    def score1w6tPOP(self, taskData):
        score = taskData['score']
        hits = taskData['hits']
        misses = taskData['misses']
        hitPoints = hits * 10
        missPoints = misses * 5
        total = hitPoints - missPoints
        pops = (total - score) // 10
        shots = hits + misses
        hits = hits - pops
        acc = hits / shots
        performance = self.performanceFunction(acc)
        self.stats['acc'] = acc
        return performance

    @log
    def convolve(self, x, y, performance):
        stepLen = self.setStepLen()
        base = self.trainers[y][x]['lockVal']
        step = performance - base
        step = step * stepLen
        lockValMatrix = self.getMatrix('lockVal')
        stepMatrix = np.ones((self.conv.xLen, self.conv.yLen))
        stepMatrix = self.conv(stepMatrix, {'x': x, 'y': y})
        stepMatrix = stepMatrix * step
        lockValMatrix = lockValMatrix + stepMatrix
        self.setMatrix('lockVal', lockValMatrix)
        return lockValMatrix

    @log
    def setStepLen(self):
        return self.stepFunc(self.runs)

    @log
    def getNameList(self):
        out = []
        for task in self.BMs:
            out.append(task['name'])
        for row in self.trainers:
            for task in row:
                out.append(task['name'])
        return out

    @log
    def getMatrix(self, key):
        out = []
        for row in self.trainers:
            line = []
            for item in row:
                line.append(item[key])
            out.append(line)
        return out

    @log
    def setMatrix(self, key, matrix):
        x = 0
        y = 0
        for row in self.trainers:
            x = 0
            for item in row:
                self.trainers[y][x][key] = matrix[y][x]
                self.trainers[y][x]['x'] = x
                self.trainers[y][x]['y'] = y
                x += 1
            y += 1
        return self.trainers


def main():
    t = taskSet('1w6tpopConfig.yaml')
    while True:
        print('RUNNING TASK')
        t.runTask()


if __name__ == '__main__':
    main()
