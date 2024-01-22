from utils import openYAML
from category import categorySet
from logger import log, logLevel, debug, info, warning, error, critical


class container:
    @log
    def __init__(self, db, config='config.yaml'):
        self.config = openYAML(config)
        self.categorySets = []
        self.categorySetConfigs = self.config['categoryConfigs']
        self.initCategories(db)

    @log
    def initCategories(self, db):
        for category in self.categorySetConfigs:
            self.categorySets.append(categorySet(category, db))

    @log
    def run(self, db):
        return self.categorySets[0].run(db)


def main():
    a = container()


if __name__ == '__main__':
    main()
