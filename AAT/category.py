from selection import taskSet
from utils import openYAML


class categorySet:
    def __init__(self, config):
        self.config = openYAML(config)
        self.taskConfigs = self.config['taskConfigs']
        self.tasks = []
        self.initTasks()

    def initTasks(self):
        for task in self.taskConfigs:
            self.tasks.append(taskSet(task))

    def run(self):
        return self.tasks[0].runTask()


def main():
    a = category('staticConfig.yaml')


if __name__ == '__main__':
    main()
    # this comment isn't bussin :(
