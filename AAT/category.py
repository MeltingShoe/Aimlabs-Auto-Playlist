from selection import taskSet
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical


class categorySet:
    @log
    def __init__(self, config, db):
        self.config = openYAML(config)
        self.taskConfigs = self.config['taskConfigs']
        self.tasks = []
        self.initTasks(db)
        self.totalRuns = 0

    @log
    def initTasks(self, db):
        for task in self.taskConfigs:
            self.tasks.append((taskSet(task, db)))

    @log
    def run(self, db):
        return self.tasks[0].runTask(db)

    @log
    def calcTotalRatio(self):
        total = 0
        for task in self.tasks:
            total += task.targetRatio
        return total

    def calcTotalWeight(self):
        total = 0
        for task in self.tasks:
            total += task.calcRatioWeight()
        return total


def main():
    a = category('staticConfig.yaml')


if __name__ == '__main__':
    main()
