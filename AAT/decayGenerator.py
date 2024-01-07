
from functionGenerator import func

# 2 modes, binary and ratio
# in binary we just have a set max runs and return a value that grow to 1 up to that max
# in ratio we can have multiple options and we increase the chance of getting less recently played scenarios while also adjusting the weights to give a target ratio of each selection
# so the oldest task might not be the highest chance if the ratio of plays is over the target
# For each choice we calculate the error in the ratio. The lower the total error the more heavily we weight by inverse recency
# So when all the ratios are within like 5% of the target we just go off order and give weight to the task we haven't played in the longest
# We should also have some sort of cap, but we need to make sure it doesn't allow for patterns to develop
# So it should be a thing like "max difference in runs since last played"
# so if it's like 15 and one task has 20 runs since last and the second most is only 5 since last it'll force that choice, maybe make this another scaled function lmao
# we want to be able to base a function off either runs in this selection list or total runs or both
# so if we have run a benchmark last time we did a task but we haven't done any benchmarks in the last several tasks we can give BMs weight
# We want to run both of these decay functions back to back and be able to enable either of them and define them separately
# We need to be able to enable a growth function that will make a task more likely next time
# rather than calculating sessions externally we can just do it in here by increasing the chance of a task after you get it and then each run do a function that can reset it to use normal decay
# we could use that for the unlocking decay too
# ideally we could wrap everything in a factory so each created instance can reference the total number of runs without passing it in


class decay:
    def __init__(self, config):
        self.config = config
        self.binary = config['binary']
        # in binary this is max runs before 100%, in ratio it's max difference in runs
        self.maxRuns = config['maxRuns']
        self.decayGroup = config['decayGroup']
        self.decayGroupFunc = func(config['decayGroupFunc'])
        self.decayTotal = config['decayTotal']
        self.decayTotalFunc = func(config['decayTotalFunc'])
        self.session = config['session']
        self.sessionFunc = func(config['sessionFunc'])
        self.sessionRuns = 0

    def __call__(self, x):
        return self.getResult(x)

    def getResult(self, x):
        if self.binary:
            return self.getBinary(x)
        else:
            return self.getRatio(x)

    def getBinary(self, x):

        self.decayGroupFunc(x)
        self.decayTotalFunc(x)
