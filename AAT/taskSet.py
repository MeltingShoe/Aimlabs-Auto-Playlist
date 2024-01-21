from mapClass import mapFactory
from utils import openYAML, scoreDB
from benchmarkSelector import chooseBenchmarkOrTask


class taskSet:
    @log
    def __init__(self, taskData):
        self.trainOrBenchmark = chooseBenchmarkOrTask(taskData)
        mapMaker = mapFactory(taskData)
        self.trainers = []
        for row in taskData['trainers']:
            for mapDef in row:
                # this looks confusing but we're just using the factory from mapClass.py to make all our map objects
                self.trainers.append(mapMaker(mapDef))
        self.benchmarks = []
        for row in taskData['benchmarks']:
            for mapDef in row:
                # this looks confusing but we're just using the factory from mapClass.py to make all our map objects
                self.benchmarks.append(mapMaker(mapDef))

        nameList = self.getNameList()
        mainConfig = openYAML('config.yaml')
        self.db = scoreDB(nameList, resetPoint=mainConfig['resetPoint'])

    @log
    def getNameList(self):
        out = []
        for task in self.BMs:
            out.append(task.DBname)
        for row in self.trainers:
            for task in row:
                out.append(task.DBname)
        return out
