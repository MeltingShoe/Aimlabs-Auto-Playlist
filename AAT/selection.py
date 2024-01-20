from functionGenerator import func
from utils import saveYAML, openYAML, launchTask, scoreDB, rawDB
from logger import log, logLevel, debug, info, warning, error, critical
import random
import numpy


class taskSet:
    def __init__(self, configPath):
        self.debug = True
        self.runs = 0
        self.config = openYAML(configPath)
        self.wmFunc = func(self.config['weightChanceMultiplier'])
        self.BMs = self.config['benchmarks']
        self.trainers = self.config['trainers']
        self.runsSinceBM = -3
        self.maxIntervalBM = self.config['maxIntervalBM']
        self.decayBM = func(self.config['decayBM'])
        self.convXfnc = func(self.config['convX'])
        self.convYfnc = func(self.config['convY'])
        self.scoreFunc = self.config['scoreFunc']
        self.performanceFunction = func(self.config['performanceFunction'])
        self.stats = {}
        self.lastBM = False
        self.convPositive = True
        nameList = self.getNameList()
        mainConfig = openYAML('config.yaml')
        self.db = scoreDB(nameList, resetPoint=mainConfig['resetPoint'])
        self.stepFunc = func(self.config['stepFunc'])
        self.weightFunc = func(self.config['weightFunc'])
        self.processNewScores()

    @log
    def processNewScores(self):
        while True:
            score = self.db()
            if score == False:
                break
            else:
                self.processScore(score)

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
    def processScore(self, score):
        score = self.processScoreXY(score)
        convOut = self.processResults(score, score['x'], score['y'])
        self.runs += 1
        return convOut

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
    def convX(self, x):
        if self.convPositive:
            return self.convXfnc(x)
        else:
            x = x * -1
            return self.convXfnc(x)

    @log
    def convY(self, x):
        if self.convPositive:
            return self.convYfnc(x)
        else:
            x = x * -1
            return self.convYfnc(x)

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

    @log
    def convFilter(self, x, y, step):
        xW = self.convX(x)
        yW = self.convY(y)
        w = xW * yW
        return step * w

    @log
    def setFinalWeights(self):
        self.setBaseWeights()
        wL = self.getMatrix('baseWeight')
        self.setMatrix('finalWeight', wL)

        return wL

    @log
    def selectTraining(self):
        wMatrix = self.setFinalWeights()
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
    def processBM(self, taskData, x):
        self.BMs[x]['score'] = taskData['score']

    @log
    def processResults(self, taskData, x, y):
        if y == -1:
            return self.processBM(taskData, x)
        score = self.parseScore(taskData)
        convOut = self.convolve(x, y, score)
        return convOut

    @log
    def getTrainingTask(self):
        x, y = self.selectTraining()
        return self.trainers[y][x]

    @log
    def getBMTask(self):
        index = random.randint(0, (len(self.BMs)-1))
        return self.BMs[index]

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
    def shiftConv(self, curX, curY, tarX, tarY, step):
        x = curX - tarX
        y = curY - tarY
        return self.convFilter(x, y, step)

    @log
    def setStepLen(self):
        return self.stepFunc(self.runs)

    @log
    def convolve(self, x, y, performance):
        stepLen = self.setStepLen()
        base = self.trainers[y][x]['lockVal']
        step = performance - base
        step = step * stepLen
        out = []
        if performance > 0:
            sign = 1
            self.convPositive = True
        else:
            sign = -1
            self.convPositive = False
        for rowIndex, row in enumerate(self.trainers):
            line = []
            for itemIndex, item in enumerate(row):
                adjustment = self.shiftConv(itemIndex, rowIndex, x, y, step)
                adjustment = abs(adjustment) * sign
                weightChanceMultiplier = self.wmFunc(
                    self.trainers[rowIndex][itemIndex]['lockVal'])
                adjustment = adjustment * weightChanceMultiplier
                self.trainers[rowIndex][itemIndex]['lockVal'] += adjustment
                if self.trainers[rowIndex][itemIndex]['lockVal'] < -1:
                    self.trainers[rowIndex][itemIndex]['lockVal'] = -1
                elif self.trainers[rowIndex][itemIndex]['lockVal'] > 1:
                    self.trainers[rowIndex][itemIndex]['lockVal'] = 1

                line.append(adjustment)
            out.append(line)

    @log
    def setBaseWeights(self):
        for row in self.trainers:
            for item in row:
                val = abs(item['lockVal'])
                w = self.weightFunc(val)
                item['baseWeight'] = w

    @log
    def trainOrBM(self):
        if self.runsSinceBM == -1:
            self.runsSinceBM += 1
            return True
        x = self.runsSinceBM / self.maxIntervalBM
        w = self.decayBM.getOutput(x)
        point = random.randint(0, 1000000)/1000000
        return point < w


def main():
    t = taskSet('1w6tpopConfig.yaml')
    while True:
        print('RUNNING TASK')
        t.runTask()


if __name__ == '__main__':
    main()
