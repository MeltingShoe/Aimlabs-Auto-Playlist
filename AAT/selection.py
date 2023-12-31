from functionGenerator import func
from utils import saveYAML, openYAML, launchTask, scoreDB, rawDB
import random


class taskSet:
    def __init__(self, configPath):

        self.debug = True
        self.config = openYAML(configPath)
        self.BMs = self.config['benchmarks']
        self.trainers = self.config['trainers']
        self.runsSinceBM = 0
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
        resetPoint = mainConfig['resetPoint']
        self.db = scoreDB(nameList, resetPoint=resetPoint)
        self.processNewScores()
        self.weightFunc = func(self.config['weightFunc'])

    def processNewScores(self):
        while True:
            score = self.db()
            if score == False:
                break
            else:
                self.processScore(score)

    def processScoreXY(self, score):
        for task in self.BMs:
            if score['name'] == task['name']:
                score['x'] = task['x']
                score['y'] = task['y']
                return score
        for row in self.trainers:
            for task in row:
                if score['name'] == task['name']:
                    print(score)
                    score['x'] = task['x']
                    score['y'] = task['y']
                    return score

    def processScore(self, score):
        score = self.processScoreXY(score)
        convOut = self.processResults(score, score['x'], score['y'])
        return convOut

    def getNameList(self):
        out = []
        for task in self.BMs:
            out.append(task['name'])
        for row in self.trainers:
            for task in row:
                print(task)
                out.append(task['name'])
        return out

    def convX(self, x):
        if self.convPositive:
            return self.convXfnc(x)
        else:
            x = x * -1
            return self.convXfnc(x)

    def convY(self, x):
        if self.convPositive:
            return self.convYfnc(x)
        else:
            x = x * -1
            return self.convYfnc(x)

    def parseScore(self, taskData):
        if self.scoreFunc == '1W6TPOP':
            return self.score1w6tPOP(taskData)
        raise Exception('invalid score function')

    def score1w6tPOP(self, taskData):
        score = taskData['score']
        hits = taskData['hits']
        misses = taskData['misses']
        print('PARSING', score, hits, misses)
        hitPoints = hits * 10
        missPoints = misses * 5
        total = hitPoints - missPoints
        print(hitPoints, missPoints, total)
        pops = (total - score) // 10

        shots = hits + misses
        hits = hits - pops

        acc = hits / shots

        performance = self.performanceFunction(acc)
        print(pops, misses, shots, acc, performance)
        self.stats['acc'] = acc
        if self.debug:
            print('score', score, 'accuracy', acc, 'hits',
                  hits, 'misses', misses, 'pops', pops, 'performance', performance, 'shots', shots)
        return performance

    def getMatrix(self, key):
        out = []
        for row in self.trainers:
            line = []
            for item in row:
                line.append(item[key])
            out.append(line)
        return out

    def setMatrix(self, key, matrix):
        x = 0
        y = 0
        for row in self.trainers:
            x = 0
            for item in row:
                item[key] = matrix[y][x]
                x += 1
            y += 1

    def convFilter(self, x, y, step):
        xW = self.convX(x)
        yW = self.convY(y)
        w = xW * yW
        return step * w

    def setFinalWeights(self):
        self.setBaseWeights()
        wL = self.getMatrix('baseWeight')
        self.setMatrix('finalWeight', wL)
        return wL

    def selectTraining(self):
        wMatrix = self.setFinalWeights()
        total = 0
        for row in wMatrix:
            for item in row:
                total += item
        if self.debug:
            print('WEIGHT MATRIX:')
            wm = wMatrix
            for row in wm:
                line = []
                for item in row:
                    percent = item / total
                    line.append(percent)
                print(line)
        key = random.uniform(0, total)
        if self.debug:
            print('making selection. total =', total, 'key =', key)
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
        print(key, x, y)
        raise Exception('selection failed somehow')

    def processBM(self, taskData, x):
        print('benchmark processing not implemented :)')
        return True

    def processResults(self, taskData, x, y):
        if y == -1:
            return self.processBM(taskData, x)
        score = self.parseScore(taskData)
        convOut = self.convolve(x, y, score)
        return convOut

    def getTrainingTask(self):
        x, y = self.selectTraining()
        return self.trainers[y][x]

    def getBMTask(self):
        index = random.randint(0, (len(self.BMs)-1))
        return self.BMs[index]

    def getTask(self):
        runBM = self.trainOrBM()
        self.lastBM = runBM
        if runBM:
            self.runsSinceBM = 0
            return self.getBMTask()
        else:
            self.runsSinceBM += 1
            return self.getTrainingTask()

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

    def shiftConv(self, curX, curY, tarX, tarY, step):
        x = curX - tarX
        y = curY - tarY
        return self.convFilter(x, y, step)

    def convolve(self, x, y, performance):
        if self.debug:
            print('ABOUT TO CONVOLVE, INPUT VALUES:')
            self.printMatrix(self.getMatrix('lockVal'))
        base = self.trainers[y][x]['lockVal']
        step = performance - base
        step = step * self.config['stepLen']
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
                # print(itemIndex, rowIndex, adjustment)
                adjustment = abs(adjustment) * sign
                self.trainers[rowIndex][itemIndex]['lockVal'] += adjustment
                if self.trainers[rowIndex][itemIndex]['lockVal'] < -1:
                    self.trainers[rowIndex][itemIndex]['lockVal'] = -1
                elif self.trainers[rowIndex][itemIndex]['lockVal'] > 1:
                    self.trainers[rowIndex][itemIndex]['lockVal'] = 1

                line.append(adjustment)
            out.append(line)

        if self.debug:

            print('WE HAVE CONVOLVED, OUTPUT VALUES:')
            self.printMatrix(self.getMatrix('lockVal'))

            print('ADJUSTMENT VALUES:')
            self.printMatrix(out)
        return out

    def printMatrix(self, matrix):
        for row in matrix:
            print(row)

    def setBaseWeights(self):
        for row in self.trainers:
            for item in row:
                val = abs(item['lockVal'])
                w = self.weightFunc(val)
                print('lockVal', val, 'weight', w)
                item['baseWeight'] = w

    def trainOrBM(self):
        if self.runsSinceBM == -1:
            self.runsSinceBM = 0
            return True
        x = self.runsSinceBM / self.maxIntervalBM
        w = self.decayBM.getOutput(x)
        print('runs since', self.runsSinceBM, 'bm chance: ', w)
        point = random.randint(0, 1000000)/1000000
        return point < w


def main():
    t = taskSet('1w6tpopConfig.yaml')
    while True:
        print('RUNNING TASK')
        t.runTask()


if __name__ == '__main__':
    main()
