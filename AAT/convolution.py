import numpy as np
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical


class convolution:
    def __init__(self, configFileName):  # you can feed a dict as the arg to give a config directly
        if type(configFileName) is str:
            config = openYAML(configFileName)
        elif type(configFileName) is dict:
            config = configFileName
        else:
            raise TypeError
            return False
        self.convMatrix = np.array(config['convMatrix'])
        self.xLen = config['xLen']
        self.yLen = config['yLen']

    @log
    # gonna try to do some type polymorphism, if we get a full array do a full conv but if we just get 1 number then just get it's 1 step
    def __call__(self, npArray, origin):
        if type(npArray) == numpy.ndarray:
            return self.calcConvolution(npArray, origin)
        elif type(npArray) == dict:
            return self.calcAdjustment(npArray, origin)
        else:
            critical('BRO YOU PUT THE WRONG TYPE IN CONV, HAS TO BE NUM OR NDARRAY')
            raise TypeError

    @log
    def calcAdjustment(self, data, origin):
        midX = self.xLen//2
        midY = self.yLen//2

    @log
    def cutMatrix(self, origin):
        # xLen - 1 - origin['x'] gives us the correct index to use the np.split function
        # then we take the second half of the result because result[0] is the bit of the array thats out of bounds that we want to chop
        # I guess we just do that 4 times??? Seems dumb and prolly slow
        matrix = self.convMatrix
        leftPad = self.xLen - 1
        sliceIndex = leftPad - origin['x']
        matrix = np.split(matrix, [sliceIndex], axis=1)[1]
        # Since we calculated how left the array is we can just chop off the rest
        matrix = np.split(matrix, [self.xLen], axis=1)[0]
        # do the same thing vertically
        topPad = self.yLen - 1
        sliceIndex = topPad - origin['y']
        matrix = np.split(matrix, [sliceIndex], axis=0)[1]
        matrix = np.split(matrix, [self.yLen], axis=0)[0]
        return matrix

    @log
    def calcConvolution(self, npArray, origin):
        matrix = self.cutMatrix(origin)
        out = npArray * matrix
        return out


def main():
    print('Stop manually testing, go write real tests...')
    a = np.array([[0, 1, 1.5],
                  [0.5, 0.75, 1.25],
                  [1, 2, 1.1]])
    b = np.array([[0, 2, 1, 1, 1],
                  [2, 0, 1, 1, 1],
                  [1, 1, 0, 1, 2],
                  [1, 1, 1, 10, 1],
                  [1, 1, 2, 1, 0]])
    config = {'convMatrix': b, 'xLen': 3, 'yLen': 3}
    conv = convolution(config)
    print(conv(a, {'x': 1, 'y': 1}))


if __name__ == '__main__':
    main()
