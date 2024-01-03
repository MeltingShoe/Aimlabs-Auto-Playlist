from utils import YN, saveYAML, openYAML, launchTask, getScore


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

    db = getScore()
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


def main():
    restart = YN('Start new task?')
    if restart:
        setIDs()
    runIDs(newTask=restart)
    print('config finished, exiting...')


if __name__ == '__main__':
    main()
