from selection import taskSet
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical


class categorySet:
    @log
    def __init__(self, config):
        self.config = openYAML(config)
        self.taskConfigs = self.config['taskConfigs']
        self.tasks = []
        self.initTasks()

    @log
    def initTasks(self):
        for task in self.taskConfigs:
            self.tasks.append(taskSet(task))

    @log
    def run(self):
        return self.tasks[0].runTask()


def main():
    a = category('staticConfig.yaml')


if __name__ == '__main__':
    main()
    # this comment isn't bussin :(
