from utils import openYAML


class inputListener:
    def __init__(self, config, handler):
        self.config = openYAML(config)
        self.handler = handler
        self.primaryButton = self.config['primaryButton']

    def selectTask(self):
        self.handler.selectTask()

    def playTask(self):
        self.handler.playTask()

    def checkForScore(self):
        self.handler.checkForScore()

    def scoreTask(self):
        self.handler.scoreTask()

    def skipTask(self):
        self.handler.skipTask()

    def runTask(self):
        self.handler.runTask()


def main():
    pass


if __name__ == '__main__':
    main()
