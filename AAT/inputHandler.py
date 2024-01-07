from utils import openYAML


class inputHandler:
    def __init__(self, config, container):
        self.config = openYAML(config)
        self.container = container

    def selectTask(self):
        pass

    def playTask(self):
        pass

    def scoreTask(self):
        pass

    def skipTask(self):
        pass

    def runTask(self):
        pass

    def checkForScore(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
