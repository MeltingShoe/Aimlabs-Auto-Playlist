from utils import openYAML
from category import categorySet


class container:
    def __init__(self, config='config.yaml'):
        self.config = openYAML(config)
        self.categorySets = []
        self.categorySetConfigs = self.config['categoryConfigs']
        self.initCategories()

    def initCategories(self):
        for category in self.categorySetConfigs:
            self.categorySets.append(categorySet(category))

    def run(self):
        return self.categorySets[0].run()


def main():
    a = container()


if __name__ == '__main__':
    main()
