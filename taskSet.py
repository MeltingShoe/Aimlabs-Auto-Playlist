from functionGenerator import func as func
from numpy.random import choice
import random


class task:
    # we need to pass in all the data to configure the task
    # this is performance function, decay function, scenario names/IDs, lock values, convolutions, output filter(define which scenarios propagate results to other tasks)
    # (could specify function to go from lock value to weight but we'll probably just always use the same one)
    # =============    NO WE NEED TO SPECIFY THE WEIGHT FUNCTION SO WE CAN MAKE A DIFFERENT ONE FOR BENCHMARKS    =============================
    # we have a bunch of logic for choosing a specific task before this point
    # so when we calculate decay we only have to consider runs of other tasks in the set
    # we also only need to calculate weights when the task set is chosen since we calculate decay for the whole set beforehand so weights only change when we pick this task
    # or when a convolution propagates to this task we also recalc total weight

    # choosing a task in the set is a multi-step processs
    # first we check if the last task was in this task set
    # if it was we have the data from the last parsed results saved, and we can randomly decide if we're in a session
    # once we've picked a task set we keep running it until the task has decided to end the session, and chooseTask will just return False and it'll set the flag to start a new session next time

    # if we're in a session we randomly pick between a few masks that we apply to the weight to either force small steps to slightly harder tasks or big jumps to the other side of the task space
    # we continue the session until they play worse than a bar
    # we raise this bar every run
    # so the idea is to keep playing if you're killing highscores

    # then we check how many time's we've done training tasks in this set since the last time we've done a benchmark
    # and we choose either BM or training
    # if we've never done BM before we do that
    # weights for benchmarks are different
    # we want them to mostly be affected by number of runs

    # calculate all base weights
    # apply mask for decay
    # if we're in a session apply the random session mask
    # apply constant mask
    # apply general skill mask(every run in all categories affects a value that's basically an approximation of the percentile of their overall skill)
    #    so early on we can see someone is generally worse than average and we can tune weights for tasks they haven't played much before so they end up in range
    #    we scale the weight of this mask by the total number of runs in the set
    #    cuz once we have enough runs we've got it tuned we don't need anything else
    # apply "on fire" mask
    #    thoughout a playsesh we keep track of the size of targets they're doing best in today relative to their average
    #    some days we're fast, some days we're smooth
    #    so through the day we apply a mask to try to get us to play tasks where we'll get high score
    #    in the long run we want to focus weak points and we choose weak point before we pick task
    #    but we don't want to get locked into just doing speed
    #    it should carry a bit sesh to sesh tho so we're not spending 70% of the session finding the strength
    #    so we make this mask based on the last 3-5 days of data with exponential decay applied to give recency bias
    # crazy idea
    #    whenever we start applying the on fire mask we check the result and tweak a confidence value based on if we were right
    #    so it goes up when we highscore somewhere we're on fire and goes down when we highscore someewhere we aren't
    #        need to normalize so we don't end up naturally inflating this because we're more likely to play tasks in the fire range
    #    so some players will generally fit this idea that we can predict their daily performance
    #    but players who's daily performance isn't tied to target size will eventually not have this mask applied
    #    we also track the total ratio and make sure we never lock into pure speed every time, we cap it at like 70% chance of choosing something in the fire
    # better idea for decay
    #    decay is a mask that applies to spots near the task instead of just the 1 task
    #    after running a task it and the harder versions should become more likely
    #    after running a few tasks in an area they should all become less likely
    # next step
    #
    # apply "more/less" button mask
    # apply global "more/less" button mask
    # actually that mask probably gets applied before this point so no "more/less" button mask

    # at this point we want a dev option that will normalize the weights so they add to 1 and display that

    # then we make a selection off those weights and return the task ID/name

    # when we do convolution we output a number for how much we should propagate that convolution
    # there is a filter which defines the range to start to propagate
    # so it's not just a row
    # but we only propagate a number
    # so we multiply each of the weights by the values in the output mask and add them all to get the propogation sum
    # each connection gets it's own output mask, so no need for a scaler just scale the mask
    # we can still have a scaler for ease tho
    # we can adjust that scaler by the total that has been propogated, so we can make it prop less over time
    # ofc defined with sick func generator
    # each connection also gets it's own input mask
    # the scaled value is multiplied by all of the weights in the input mask and those weights are applied to the next task

    # weight functions are 3 parts, translation from lock value to weight, decay function, and a function that combines those values
    # this way we can make the function weight the decay more heavily

    # every task is defined as a dict with ID, name, lockValue, x, y
    # don't think we need number of runs because decay is a mask
    def __init__(self, config):
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
        return {'name': name, 'ID': ID}

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
        return {'name': name, 'ID': ID}

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
                total += self.getBaseTrainWeight(task)
                num += 1
        # we're doing average instead of total, who knows this will def need tweaking
        return total/num
        # not a big deal since we'll clamp the weights too
        # might even do task order progression externally if that's simplier/this don't work

    def getBaseTrainWeight(self, task):
        lockVal = task['lockVal']
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
        return {'name': name, 'ID': ID}

    def parseScoreAndDoConvolution(self):
        pass


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
    for row in conv:
        line = ' | '
        for w in row:
            w = w*100000
            w = w//1
            w = w/100000
            w = str(w)
            while len(w) < 7:
                w += '0'
            w += ' | '
            line += w
        line += '\n'
        out += line
    print(out)


def main():
    exampleConfig = {
        'benchmarks': [{'name': 'bm0', 'ID': '1'}, {'name': 'bm1', 'ID': '2'}, {'name': 'bm2', 'ID': '3'}, {'name': 'bm3', 'ID': '4'}, {'name': 'bm4', 'ID': '5'}],
        'trainers': [[{'name': '00', 'ID': '6', 'lockVal': '0', 'x': 0, 'y': 0}, {'name': '10', 'ID': '7', 'lockVal': '0', 'x': 1, 'y': 0}, {'name': '20', 'ID': '8', 'lockVal': '0', 'x': 2, 'y': 0}, {'name': '30', 'ID': '9', 'lockVal': '-0.25', 'x': 3, 'y': 0}, {'name': '40', 'ID': '10', 'lockVal': '-0.5', 'x': 4, 'y': 0}],
                     [{'name': '01', 'ID': '11', 'lockVal': '-0.25', 'x': 0, 'y': 1}, {'name': '11', 'ID': '12', 'lockVal': '-0.25', 'x': 1, 'y': 1}, {'name': '21', 'ID': '13',
                                                                                                                                                       'lockVal': '-0.25', 'x': 2, 'y': 1}, {'name': '31', 'ID': '', 'lockVal': '-0.5', 'x': 3, 'y': 1}, {'name': '41', 'ID': '15', 'lockVal': '-0.5', 'x': 4, 'y': 1}],
                     [{'name': '02', 'ID': '16', 'lockVal': '-0.5', 'x': 0, 'y': 2}, {'name': '12', 'ID': '17', 'lockVal': '-0.5', 'x': 1, 'y': 2}, {'name': '22', 'ID': '18',
                                                                                                                                                     'lockVal': '-0.5', 'x': 2, 'y': 2}, {'name': '32', 'ID': '19', 'lockVal': '-1', 'x': 3, 'y': 2}, {'name': '42', 'ID': '20', 'lockVal': '-1', 'x': 4, 'y': 2}],
                     [{'name': '03', 'ID': '21', 'lockVal': '-1', 'x': 0, 'y': 3}, {'name': '13', 'ID': '22', 'lockVal': '-1', 'x': 1, 'y': 3}, {'name': '23', 'ID': '23',
                                                                                                                                                 'lockVal': '-1', 'x': 2, 'y': 3}, {'name': '33', 'ID': '24', 'lockVal': '-1', 'x': 3, 'y': 3}, {'name': '43', 'ID': '25', 'lockVal': '-1', 'x': 4, 'y': 3}],
                     [{'name': '04', 'ID': '26', 'lockVal': '-1', 'x': 0, 'y': 4}, {'name': '14', 'ID': '27', 'lockVal': '-1', 'x': 1, 'y': 4}, {'name': '24', 'ID': '28', 'lockVal': '-1', 'x': 2, 'y': 4}, {'name': '34', 'ID': '29', 'lockVal': '-1', 'x': 3, 'y': 4}, {'name': '44', 'ID': '30', 'lockVal': '-1', 'x': 4, 'y': 4}]],
        'trainWeightFunc': {'inputRanges': [-1, -0.2, 0, 0.2, 1], 'outputRanges': [0.05, 1, 1, 1, 0.05], 'scales': [1, 1, 1, 1]},
        'xConvTrain': {'inputRanges': [-1, -0.4, 0, 1], 'outputRanges': [1.2, 1.2, 1, 0.75], 'scales': [0, 0, 1.5]},
        'yConvTrain': {'inputRanges': [-1, -0.4, 0, 1], 'outputRanges': [1.2, 1.2, 1, 0.75], 'scales': [0, 0, 1.5]},
        'convTrainRange': 4,
        'decayTrain': {'inputRanges': [0, 1], 'outputRanges': [1, 0], 'scales': [0]},
        'decayRange': 3,
        'decayBM': {'inputRanges': [0, 1], 'outputRanges': [0.05, 0.85], 'scales': [2]},
        'maxIntervalBM': 10,
        'decayFunc': {'inputRanges': [0, 0.7, 1], 'outputRanges': [0, 1, 0.85], 'scales': [1, -1]},
        'decayInterval': 15
    }

    testTaskSet = task(exampleConfig)
    for i in range(100):
        print(testTaskSet.chooseTask())
        acc = random.randint(650, 1000)/1000
        print('acc', acc)


if __name__ == '__main__':
    main()
