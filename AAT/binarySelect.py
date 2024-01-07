import random
from functionGenerator import func


class selectBin:
    def __init__(self, config):
        self.decay = func(config)  # output of decay func must be 0-1

    def __call__(self, x):
        return self.getOutput(x)

    def getOutput(self, x):
        key = random.uniform(0, 1)
        target = self.decay(x)
        return key < target
