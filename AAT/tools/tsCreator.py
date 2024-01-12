from utils import YN, saveYAML, openYAML, launchTask, rawDB


class setIDs:
    def __init__(self):
        self.idList = []
        self.populateList()

    def addID(self):
        print('input workshop ID number '+str(len(self.idList))
              + '.      |  Press B for back, type YES(case sensitive) when done')
        ID = input()
        if ID == '':
            print('empty input')
            return False
        if ID == 'b' or ID == 'B':
            self.idList.pop(-1)
            return False
        if ID == 'YES':
            return True
        self.idList.append(ID)
        return False

    def populateList(self):
        while True:
            if self.addID():
                self.saveList()
                print('list saved')
                return True

    def saveList(self):
        saveYAML(self.idList, 'wsIDs.yaml')


def runIDs(newTask=True):

    db = rawDB()
    IDs = openYAML('wsIDs.yaml')

    taskConfig = []
    i = 0
    while i < len(taskConfig):
        i += 1
    while i < len(IDs):
        print(
            'launching task, input YES to continue or anything else to relaunch. ID = ', IDs[i])
        launchTask(int(IDs[i]))
        inp = input()
        if inp != 'YES':
            continue
        print('size?')
        size = input()
        print('speed/difficulty?(type BM for benchmark)')
        difficulty = input()
        print('run task then type YES to continue, or anything else to relaunch task and restart')
        inp = input()
        if inp != 'YES':
            continue
        data = db.score()
        new = data[0]
        data = data[1]
        if new == False:
            print('no new data, relaunching task and restarting')
            continue
        name = data['name']
        print('data read, score =', data['score'])
        out = {
            'name': name,
            'ID': IDs[i],
            'size': size,
            'difficulty': difficulty,
        }
        i += 1
        taskConfig.append(out)
    print('all IDs done, printing output')
    print(taskConfig)
    print('saving data')
    saveYAML(taskConfig, 'tmpTaskConfig.yaml')


def inputVals(prompt):
    i = 0
    out = []
    while True:
        print(i, prompt)
        val = input()
        if val == 'YES':
            return out
        out.append(val)
        i += 1


def parseTask():
    data = openYAML('inputConfig.yaml')
    sizes = inputVals('size?')
    speeds = inputVals('speed?')
    bms = []
    trainers = []
    x = 0
    y = -1
    for r in sizes:
        for item in data:
            if item['difficulty'] == 'BM' and item['size'] == r:
                val = item
                val['x'] = x
                val['y'] = y
                val['scores'] = []
                val['ID'] = int(val['ID'])
                bms.append(val)
                x += 1
    y += 1
    x = 0
    for t in speeds:
        line = []
        x = 0
        for r in sizes:
            for item in data:
                if item['difficulty'] == t and item['size'] == r:
                    print('IN IT =====================================================')
                    val = item

                    val['x'] = x
                    val['y'] = y
                    val['ID'] = int(val['ID'])
                    val['lockVal'] = -1

                    print(val)

                    line.append(val)
                    x += 1

        trainers.append(line)
        y += 1
    out = {
        'BMs': bms,

        'trainers': trainers
    }
    saveYAML(out, 'outputConfig.yaml')
    print(out)


def main():
    p = YN('Parse task?')
    if p:
        parseTask()
        print('we did it :)')
        return True
    restart = YN('Start new task?')
    if restart:
        setIDs()
    runIDs(newTask=restart)
    print('config finished, exiting...')
    return True


if __name__ == '__main__':
    main()
