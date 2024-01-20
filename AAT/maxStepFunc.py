from functionGenerator import func


class step:
    def __init__(self, stepFuncDef):
        self.runs = 0
        self.stepFunc = func(stepFuncDef)

    def __call__(self):
        return self.getMaxStep()

    def getMaxStep(self):
        step = self.stepFunc(self.runs)
        self.runs += 1
        return step
