import math
import matplotlib.pyplot as plt


class func:
    def __init__(self, definition):
        self.definition = definition
        self.inputRanges = definition['inputRanges']
        self.outputRanges = definition['outputRanges']
        self.scales = definition['scales']

    def plotFunction(self, samples=1000, oversamples=100):

        start = self.inputRanges[0]
        stop = self.inputRanges[-1]
        step = (stop - start)/samples
        start = start - (step*oversamples)
        stop = stop + (step*oversamples)
        xs = []
        ys = []
        x = start
        while x <= stop:
            xs.append(x)
            y = self.getOutput(x)
            ys.append(y)
            x += step
        plt.plot(xs, ys)
        plt.show()

    def getOutput(self, x):
        if x < self.inputRanges[0]:
            x = self.inputRanges[0]
        if x > self.inputRanges[-1]:
            x = self.inputRanges[-1]
        lowI = self.getRange(x)
        rangeData = self.getRangeData(lowI)
        if rangeData == -1:
            return self.outputRanges[0]
        if rangeData['xHigh'] == 'inf':

            return self.outputRanges[-1]
        up = True
        if rangeData['yLow'] > rangeData['yHigh']:
            up = False
        normX = self.getXPercent(x, rangeData)
        normY = self.curve(normX, rangeData['scale'], up)
        outY = self.scaleY(normY, rangeData)
        return outY

    def getXPercent(self, x, rangeData):
        low = rangeData['xLow']
        high = rangeData['xHigh']
        return((x-low)/(high-low))

    def scaleY(self, normY, rangeData):
        low = rangeData['yLow']
        high = rangeData['yHigh']
        width = abs(high - low)
        scaled = normY*width
        shifted = scaled + min([high, low])
        return shifted

    def getRange(self, x):
        i = 0
        while i < len(self.inputRanges):
            if x <= self.inputRanges[i]:
                return i-1
            i += 1
        return i

    def getRangeData(self, lowIndex):
        if lowIndex == -1 or lowIndex > len(self.inputRanges):
            return -1
        out = {
            'xLow': self.inputRanges[lowIndex],
            'yLow': self.outputRanges[lowIndex],
            'scale': self.scales[lowIndex]
        }
        if lowIndex == len(self.inputRanges):
            out['xHigh'] = 'inf'
            out['yHigh'] = 'inf'
        else:
            out['xHigh'] = self.inputRanges[lowIndex+1]
            out['yHigh'] = self.outputRanges[lowIndex+1]
        return out

    def exp(self, x, scale=1, up=True):
        if not up:
            x = 1-x
        scale = 1+scale
        y = x ** scale
        '''if not up:
                                    return 1-y'''
        return y

    def sqrt(self, x, scale=1, up=True):
        if not up:
            x = 1-x

        scale = 1+scale
        scale = 1/scale
        y = x ** scale
        '''if not up:
                                    return 1-y'''
        return y

    def curve(self, x, scale=0, up=True):
        if scale == 0:
            if up:
                return x
            return 1-x
        if scale > 0:
            return self.exp(x, scale, up)
        if scale < 0:
            return self.sqrt(x, abs(scale), up)
        print('how did we get here???')


def main():
    exampleDefinition2 = {
        'inputRanges': [-1, -0.4, 0, 1],
        'outputRanges': [1.2, 1.2, 1, 0.75],
        'scales': [0, 0, 1.5]
    }

    f = func(exampleDefinition2)

    f.plotFunction()


if __name__ == '__main__':
    main()
