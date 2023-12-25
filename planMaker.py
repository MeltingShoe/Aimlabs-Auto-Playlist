import yaml
import math
import matplotlib.pyplot as plt


def makeTaskList():
    print('num BMs?')
    bmNum = int(input())
    print('x?')
    xNum = int(input())
    print('y?')
    yNum = int(input())
    i = 0
    bmList = []
    while i < bmNum:
        iStr = str(i)
        print('BM'+iStr+' name?')
        name = input()
        print('BM'+iStr+' ID?')
        ID = input()
        bmList.append({'name': name, 'ID': ID})
        i += 1
    x = 0
    y = 0
    trainerList = []
    while y < yNum:
        row = []
        x = 0
        while x < xNum:

            print('X'+str(x)+' Y'+str(y)+' name?')
            name = input()
            print('X'+str(x)+' Y'+str(y)+' ID?')
            ID = input()
            print('X'+str(x)+' Y'+str(y)+' lockVal?')
            lockVal = input()
            row.append({'name': name, 'ID': ID,
                        'lockVal': lockVal, 'x': x, 'y': y})
            x += 1
        trainerList.append(row)
        y += 1
        print(y)

    with open('taskList.txt', 'w') as f:
        f.write(str({'BMs': bmList, 'trainers': trainerList}))
    return {'BMs': bmList, 'trainers': trainerList}


def main():
    out = makeTaskList()
    print(out)


if __name__ == '__main__':
    main()
