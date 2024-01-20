import random
from functionGenerator import func


class chooseBenchmarkOrTask:
    def __init__(self, config):
        self.decayFunction = func(config['decayBM'])
        self.runsSinceBM = config['startRuns'] if config['startRuns'] is not None else -3
        self.maxInterval = self.config['maxIntervalBM']

    @log
    def __call__(self):
        return self.makeSelection()

    @log
    def makeSelection(self):
        if self.runsSinceBM <= -1:
            self.runsSinceBM += 1
            return True
        percentOfMaxInterval = self.runsSinceBM / self.maxIntervalBM
        BMweight = self.decayFunction(percentOfMaxInterval)
        key = random.uniform(0, 1)
        return key < BMweight
