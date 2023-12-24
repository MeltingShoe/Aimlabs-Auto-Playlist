import yaml
import math
import matplotlib.pyplot as plt
taskCategories = ['static', 'target acquisition', 'follow up', 'speed dynamic clicking', 'evasive dynamic clicking',
                  'smooth tracking', 'precise tracking', 'reactive tracking', 'speed target switching', 'evasive target switching']
taskVariations = ['normal', 'close', 'far', 'incline']

# you can just add shit without thinking about structure and separate it out later it'll be fine trust

# individual task types are represented as nested lists. higher items(lower number in outer list) are longer duration(for static at least) with top row being benchmarks
# further left items(smaller index in inner list) are larger
# so easiest is top left and hardest is bottom right
# this structure is used for scenario IDs and also masks like the locked matrix
# should prolly use numpy


# np.random.choice( 1DIM CHOICE ARRAY, p=1DIM WEIGHT ARRAY)
# could also just random gen from 0 to the total of all weights then add up to that number


class scenario:
    def __init__(self, name, ID, constAdder=0, lowBound=0.05, highBound=0.8, maxRuns=6, runDecay=0.25, runs=0, lockValue=-1.0):

        self.name = name
        self.ID = ID
        self.constAdder = constAdder
        # tracking number of runs since we last ran would be terrible because we'd have to increment every task every time
        # instead we can track runs, make it more likely to do tasks with less runs, and IG decrement them all when they're all over 1
        self.runs = runs
        self.lockValue = lockValue
        self.lowBound = lowBound
        self.highBound = highBound
        self.maxRuns = maxRuns
        self.runDecay = runDecay
        # self.passValue = 0.0 I think we can do OG plan of just having lock and pass be 1 var and weight is higher the closer to 0.
        # I don't remember why I thought it was important to split those 2 up but I'm sure I'll find out soon

    def getBaseWeight(self):
        w = abs(self.lockValue)
        w = 1-w
        w = w/self.highBound

        scale = self.maxRuns/(self.runs + 1)
        scale = math.log(scale, self.maxRuns)

        w = w * scale

        if w >= 1:
            w = 1
        elif w < self.lowBound:
            w = self.lowBound

        w = w + (w * self.constAdder)

        return w

    # -0.2 to 0.2 is in optimal training range, so target should be 1 if over range, -1 if under range, or 0 if in range
    def adjustLockValue(self, targetVal):
        self.lockValue = (self.lockValue + targetVal)/2

    # convWeight is the weight of the convolution filter
    def tuneWeight(self, targetVal, convWeight):
        self.lockValue = (
            self.lockValue + (targetVal * convWeight))/(1+convWeight)

    # those other tuning functions are bad, we should always just add weight tbh,
    # pulling it to a value complicates things i think
    # and we should probably calculate the effect of the convolution outside of here
    def addWeight(self, weight):
        self.lockValue += weight

    def decayRuns(self):
        self.runs = self.runs - self.runDecay
        if self.runs < 0:
            self.runs = 0

    def pairSelectionStep(self):
        weight = self.getBaseWeight()
        self.decayRuns()
        return weight

    def taskSelected(self):
        self.runs += 1
        out = {
            "ID": self.ID,
            "name": self.name
        }
        return out


class task:
    def __init__(self, xNum, yNum, bmNum):
        self.xNum = xNum
        self.yNum = yNum
        self.bmNum = bmNum
        self.scenarioList = [[False for i in range(xNum)] for i in range(yNum)]
        self.bmList = [False for i in range(bmNum)]

    def setScenario(self, x, y, name, ID, constAdder=0, lowBound=0.05, highBound=0.8, maxRuns=7, runDecay=0.25, runs=0, lockValue=-1.0):
        self.scenarioList[y][x] = scenario(
            name, ID, constAdder, lowBound, highBound, maxRuns, runDecay, runs, lockValue)

    def getScenario(self, x, y):
        return self.scenarioList[y][x]


class dictFactory:
    def __init__(self):
        print('constant to add?')
        self.constAdder = input()

        self.runs = '0'
        print('lockValue?')
        self.lockValue = input()

    def makeDict(self):
        print('name?')
        name = input()
        print('ID?')
        ID = input()
        a = {
            'name': name,
            'ID': ID,
            'constAdder': self.constAdder,
            'runsSinceLast': self.runs,
            'lockValue': self.lockValue
        }
        return a


def makeTaskConfig():
    print('task set name?')
    taskName = input()
    print('X?')
    xNum = int(input())
    print('Y?')
    yNum = int(input())
    print('number of benchmarks?')
    bmNum = int(input())
    print('lowbound?')
    self.lowBound = input()
    print('highBound?')
    self.highBound = input()
    print('max runs?')
    self.maxRuns = input()
    print('decay?')
    self.runDecay = input()
    factory = dictFactory()
    bms = []
    print('Enter benchmarks')
    for i in range(bmNum):
        bms.append(factory.makeDict())
    tasks = []
    print('Enter training tasks')
    for i in range(yNum):
        row = []
        for j in range(xNum):
            row.append(factory.makeDict())
        tasks.append(row)
    a = {
        'taskName': taskName,
        'benchmarks': bms,
        'trainingTasks': tasks,
        'lowBound': self.lowBound,
        'highBound': self.highBound,
        'maxRuns': self.maxRuns,
        'runDecay': self.runDecay,
    }
    fName = taskName + '.yaml'
    file = open(fName, "w")
    yaml.dump(a, file)
    file.close()
    return a


# make console UI for config creation
# first it asks for default values for stuff like lowbound and decay, a name for the task set, and the x/y and number of benchmarks
# then you can select the x/y of a task and then modify all of it's values
# for each set we'll need to be able to choose the performance metric function for the benchmark and training tasks
# we also define convolutions for the benchmarks and tasks
# once we can do all that we add a GUI
# connections between task types propagate the convolution to a different task set
# for each connection you define a scalar and the row to start propagating.
# so you could make weak connections or connections which only start to affect the next task once you're towards the bottom
# maybe you can also define a different filter pattern to apply IDK
# we should probably add a confidence factor that defines how big the steps we take are
# could save everything in sqlite since we have to use it anyway, using a full on db is prolly extra tho
o
