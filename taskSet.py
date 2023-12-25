from functionGenerator import func as func
from numpy.random import choice
import random
import yaml


class task:

    def __init__(self, config):
        self.taskSetName = config['taskSetName']
        self.BMs = config['benchmarks']
        self.trainers = config['trainers']
        self.trainWeightFunc = func(config['trainWeightFunc'])
        self.xConvTrain = func(config['xConvTrain'])
        self.yConvTrain = func(config['yConvTrain'])
        self.decayTrain = func(config['decayTrain'])
        self.decayRange = config['decayRange']
        self.decayBM = func(config['decayBM'])
        self.maxIntervalBM = config['maxIntervalBM']
        self.decayFunc = func(config['decayFunc'])
        self.decayInterval = config['decayInterval']
        self.propagateMask = config['propagateMask']
        self.convTrainRange = config['convTrainRange']
        self.xTrainScale = func(config['xTrainScale'])
        self.yTrainScale = func(config['yTrainScale'])
        self.trainWeightRange = config['trainWeightRange']
        self.performanceFunction = func(config['performanceFunction'])
        self.maxStep = config['maxStep']

        self.convDecay = createConv(
            self.decayRange, self.decayTrain.getOutput, self.decayTrain.getOutput)

        self.decayMask = self.getInitialDecay()

        self.runsSinceBM = -1
        self.rowNum = len(self.trainers)
        self.columnNum = len(self.trainers[0])
        self.BMNum = len(self.BMs)
        self.convTrain = createConv(
            self.rowNum-1, self.xConvTrain.getOutput, self.yConvTrain.getOutput)

    def chooseBM(self):
        selection = choice(self.BMs, 1)
        self.runsSinceBM = 0
        name = selection[0]['name']
        ID = selection[0]['ID']
        x = selection[0]['x']
        y = selection[0]['y']
        return {'name': name, 'ID': ID, 'x': x, 'y': y}

    def getFinalWeight(self):
        out = []
        self.addDecay()
        decay = self.calcDecay()
        for row in self.trainers:
            line = []
            for task in row:
                base = self.getBaseTrainWeight(task)
                line.append(base)

            out.append(line)

        finalOut = self.applyDecay(out, decay)
        return finalOut

    def chooseTrainingTask(self):
        self.runsSinceBM += 1
        weights = self.getFinalWeight()
        w = []
        for row in weights:
            for item in row:
                w.append(item)
        tasks = []
        for row in self.trainers:
            for item in row:
                tasks.append(item)
        w = weightsToPercents(w)
        selection = choice(tasks, 1, p=w)
        y = selection[0]['y']
        x = selection[0]['x']
        name = selection[0]['name']
        ID = selection[0]['ID']
        self.subDecay(x, y)
        return {'name': name, 'ID': ID, 'x': x, 'y': y}

    def addDecay(self):
        out = []
        step = 1 / self.decayInterval
        for row in self.decayMask:
            line = []
            for weight in row:
                line.append(weight+step)
            out.append(line)
        self.decayMask = out
        return out

    def subDecay(self, x, y):
        homeX = x
        homeY = y
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        i = -1
        j = 0
        x = 0
        y = 0
        mask = self.decayMask
        conv = self.convDecay
        for row in mask:
            for item in row:
                if abs(x - homeX) < self.decayRange:
                    if i == -1:
                        i = 0
                    try:
                        mask[y][x] -= conv[i][j]
                    except:
                        print('exception lol')
                    j += 1
                x += 1
            y += 1
            if i != -1:
                i += 1
        self.decayMask = mask
        return mask

    def calcDecay(self):
        out = []
        for row in self.decayMask:
            line = []
            for item in row:
                val = self.decayFunc.getOutput(item)
                line.append(val)
            out.append(line)

        return out

    def applyDecay(self, inp, mask):
        i = 0
        j = 0
        out = []
        while i < len(inp):
            line = []
            j = 0
            while j < len(inp[0]):
                val = inp[i][j] * mask[i][j]
                line.append(val)
                j += 1
            out.append(line)
            i += 1
        return out

    def getEmptyList(self):
        out = []
        for row in self.trainers:
            line = []
            for item in row:
                line.append(0)
            out.append(line)
        return out

    def getInitialDecay(self):
        out = []
        for row in self.trainers:
            line = []
            for item in row:
                line.append(1)
            out.append(line)
        return out

    def trainOrBM(self):
        if self.runsSinceBM == -1:
            self.runsSinceBM = 0
            return True
        x = self.runsSinceBM / self.maxIntervalBM
        w = self.decayBM.getOutput(x)
        print('runs since', self.runsSinceBM, 'bm chance: ', w)
        point = random.randint(0, 1000000)/1000000
        return point < w

    def getAverageWeight(self):
        total = 0
        num = 0
        for task in self.BMs:
            # important that we choose weights before applying decay, since the task set is decayed too
            total += self.getBaseBMWeight(task)
            num += 1
        for row in self.trainers:
            for task in row:
                o = task['lockVal']
                total += self.getBaseTrainWeight(o)
                num += 1
        # we're doing average instead of total, who knows this will def need tweaking
        return total/num
        # not a big deal since we'll clamp the weights too
        # might even do task order progression externally if that's simplier/this don't work

    def getBaseTrainWeight(self, lockVal):
        if type(lockVal) == dict:
            lockVal = lockVal['lockVal']
        weight = self.trainWeightFunc.getOutput(float(lockVal))
        return weight

    def getBaseBMWeight(self, task):
        lockVal = task['lockVal']
        weight = self.BMweightFunc(lockVal)
        return weight

    def chooseTask(self):
        runBM = self.trainOrBM()
        if runBM:
            task = self.chooseBM()
        else:
            task = self.chooseTrainingTask()
        name = task['name']
        ID = task['ID']
        x = task['x']
        y = task['y']
        return {'name': name, 'ID': ID, 'x': x, 'y': y}

    def parseScore(self, acc):
        return self.performanceFunction.getOutput(acc)

    # this calculates the matrix of scaled scores IE harder tasks target scores slightly lower
    def warpScore(self, score, x, y):
        out = []
        for i in range(0, len(self.trainers)):
            line = []
            for j in range(0, len(self.trainers[0])):
                width = j - x
                inX = width / self.convTrainRange
                inX = self.xConvTrain.getOutput(inX)
                height = i - y
                inY = height / self.convTrainRange
                inY = self.yConvTrain.getOutput(inY)
                val = inX * inY
                val = val * score
                line.append(val)
            out.append(line)
        return out

    def warpWeights(self, x, y):
        out = []
        for i in range(0, len(self.trainers)):
            line = []
            for j in range(0, len(self.trainers[0])):
                width = j - x
                inX = width / self.trainWeightRange
                inX = self.xTrainScale.getOutput(inX)
                height = i - y
                inY = height / self.trainWeightRange
                inY = self.yTrainScale.getOutput(inY)
                val = inX * inY
                line.append(val)
            out.append(line)
        return out

    def processOutput(self, acc, x, y):

        score = self.parseScore(acc)
        if y == -1:
            return score
        scoreMatrix = self.warpScore(score, x, y)
        weightMatrix = self.warpWeights(x, y)
        out = []
        for i in range(0, len(self.trainers)):
            line = []
            for j in range(0, len(self.trainers[0])):
                w = self.stepWeight(
                    self.trainers[i][j]['lockVal'], scoreMatrix[i][j], weightMatrix[i][j])
                self.trainers[i][j]['lockVal'] = w
                line.append(w)
            out.append(line)
        return out

    def stepWeight(self, base, target, weight):
        total = target - float(base)
        step = total*self.maxStep
        step = step * weight
        out = float(base) + step
        return out


def returnZero(dummyVal):
    return 0


def createConv(radius, xFunc, yFunc):
    x = radius * -1
    y = radius * -1
    conv = []
    while y <= radius:
        x = radius * -1
        row = []
        while x <= radius:
            xOut = xFunc(x/radius)
            yOut = yFunc(y/radius)
            out = xOut * yOut
            row.append(out)
            x += 1
        conv.append(row)
        y += 1
    return conv


def weightsToPercents(weights):
    total = 0
    for weight in weights:
        total += weight
    out = []
    count = 0
    for weight in weights:
        perc = weight / total
        count += perc
        out.append(perc)
    return out


def printConv(conv):
    out = ''
    total = 0
    for row in conv:
        for w in row:
            total += w
    for row in conv:
        line = ' | '
        for w in row:
            # w = w/total
            w = w*1000
            w = w//1
            w = str(int(w))

            w += ' | '
            line += w
        line += '\n'
        out += line
    print(out)


def resetConfig():
    exampleConfig = {
        'taskSetName': 'reflex shot',
        'benchmarks': [{'name': 'bm0', 'ID': '1', 'y': -1, 'x': 0}, {'name': 'bm1', 'ID': '2', 'y': -1, 'x': 1}, {'name': 'bm2', 'ID': '3', 'y': -1, 'x': 2}, {'name': 'bm3', 'ID': '4', 'y': -1, 'x': 3}, {'name': 'bm4', 'ID': '5', 'y': -1, 'x': 4}],
        'trainers': [[{'name': '00', 'ID': '6', 'lockVal': '0', 'x': 0, 'y': 0}, {'name': '10', 'ID': '7', 'lockVal': '0', 'x': 1, 'y': 0}, {'name': '20', 'ID': '8', 'lockVal': '0', 'x': 2, 'y': 0}, {'name': '30', 'ID': '9', 'lockVal': '-0.25', 'x': 3, 'y': 0}, {'name': '40', 'ID': '10', 'lockVal': '-0.5', 'x': 4, 'y': 0}],
                     [{'name': '01', 'ID': '11', 'lockVal': '-0.25', 'x': 0, 'y': 1}, {'name': '11', 'ID': '12', 'lockVal': '-0.25', 'x': 1, 'y': 1}, {'name': '21', 'ID': '13',
                                                                                                                                                       'lockVal': '-0.25', 'x': 2, 'y': 1}, {'name': '31', 'ID': '', 'lockVal': '-0.5', 'x': 3, 'y': 1}, {'name': '41', 'ID': '15', 'lockVal': '-0.5', 'x': 4, 'y': 1}],
                     [{'name': '02', 'ID': '16', 'lockVal': '-0.5', 'x': 0, 'y': 2}, {'name': '12', 'ID': '17', 'lockVal': '-0.5', 'x': 1, 'y': 2}, {'name': '22', 'ID': '18',
                                                                                                                                                     'lockVal': '-0.5', 'x': 2, 'y': 2}, {'name': '32', 'ID': '19', 'lockVal': '-1', 'x': 3, 'y': 2}, {'name': '42', 'ID': '20', 'lockVal': '-1', 'x': 4, 'y': 2}],
                     [{'name': '03', 'ID': '21', 'lockVal': '-1', 'x': 0, 'y': 3}, {'name': '13', 'ID': '22', 'lockVal': '-1', 'x': 1, 'y': 3}, {'name': '23', 'ID': '23',
                                                                                                                                                 'lockVal': '-1', 'x': 2, 'y': 3}, {'name': '33', 'ID': '24', 'lockVal': '-1', 'x': 3, 'y': 3}, {'name': '43', 'ID': '25', 'lockVal': '-1', 'x': 4, 'y': 3}],
                     [{'name': '04', 'ID': '26', 'lockVal': '-1', 'x': 0, 'y': 4}, {'name': '14', 'ID': '27', 'lockVal': '-1', 'x': 1, 'y': 4}, {'name': '24', 'ID': '28', 'lockVal': '-1', 'x': 2, 'y': 4}, {'name': '34', 'ID': '29', 'lockVal': '-1', 'x': 3, 'y': 4}, {'name': '44', 'ID': '30', 'lockVal': '-1', 'x': 4, 'y': 4}]],
        'propagateMask': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0.5], [0, 0, 0, 0.5, 1], [0.5, 0.5, 0.5, 1, 1], [1, 1, 1, 1, 1]],
        'trainWeightFunc': {'inputRanges': [-1, -0.2, 0, 0.2, 1], 'outputRanges': [0.05, 1, 1, 1, 0.05], 'scales': [1, 1, 1, 1]},
        'xConvTrain': {'inputRanges': [-1, -0.4, 0, 1], 'outputRanges': [1.2, 1.2, 1, 0.75], 'scales': [0, 0, 1.5]},
        'yConvTrain': {'inputRanges': [-1, -0.4, 0, 1], 'outputRanges': [1.2, 1.2, 1, 0.75], 'scales': [0, 0, 1.5]},
        'convTrainRange': 3,
        'decayTrain': {'inputRanges': [0, 1], 'outputRanges': [1, 0], 'scales': [0]},
        'decayRange': 1,
        'decayBM': {'inputRanges': [0, 1], 'outputRanges': [0.05, 0.85], 'scales': [2]},
        'maxIntervalBM': 15,
        'decayFunc': {'inputRanges': [0, 0.7, 1], 'outputRanges': [0, 1, 0.85], 'scales': [1, -1]},
        'decayInterval': 5,
        'xTrainScale': {'inputRanges': [-1, 0, 0.2, 0.4, 1], 'outputRanges': [1, 1, 0.7, 0.2, 0], 'scales': [0, 0, 0, 0]},
        'yTrainScale': {'inputRanges': [-1, 0, 0.2, 0.4, 1], 'outputRanges': [1, 1, 0.7, 0.2, 0], 'scales': [0, 0, 0, 0]},
        'trainWeightRange': 3,
        'performanceFunction': {'inputRanges': [0, 0.7, 0.75, 0.88, 0.92, 0.97], 'outputRanges': [-1, -1, -0.2, 0, 0.2, 1], 'scales': [0, 0, 0, 0, 0, 0, 0, 0, 0]},
        'maxStep': 0.6
    }
    saveYAML(exampleConfig)


def saveYAML(config):
    file = open("config.yaml", "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


def openYAML():

    with open("config.yaml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def main():
    resetConfig()

    config = openYAML()
    testTaskSet = task(config)
    for i in range(100):

        selection = testTaskSet.chooseTask()
        print(selection)
        #acc = random.randint(800, 1000)/1000
        #print('acc', acc)
        acc = float(input())
        if selection['name'][0] != 'b':
            newWeights = testTaskSet.processOutput(
                acc, selection['x'], selection['y'])
            printConv(newWeights)


if __name__ == '__main__':
    main()
