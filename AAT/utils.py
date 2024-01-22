import yaml
import os
import sqlite3
import webbrowser
import ast
from logger import log, logLevel, debug, info, warning, error, critical, logger_instance


@log
def configPath(path):
    exists = os.path.isfile(os.path.abspath(os.path.join(
        os.getcwd(), os.pardir, 'config', path)))
    if exists:
        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, 'config', path))
    else:
        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, 'config/modelConfig', path))
    return path


@log
def saveYAML(config, path):
    path = configPath(path)
    file = open(path, "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


@log
def openYAML(path):
    path = configPath(path)
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


config = openYAML('devConfig.yaml')
block = config['blockTaskLaunch']
confirm = config['confirmToRunBlockedFunctions']


@log
def devBlock(func):
    if not block:
        return func
    if not confirm:
        def nop(*args, **kwargs):
            pass
        return nop

    def wrap(*args, **kwargs):
        if YN('Function blocked, run function?'):
            func(*args, **kwargs)
    return wrap


@devBlock
def launchTask(ID):
    url = 'aimlab://workshop?id='
    url += str(ID)
    webbrowser.open(url)


@log
def YN(prompt):
    if type(prompt) != str:
        print('bad prompt type')
        exit()
    print(prompt, '(Y/N)')
    a = input()
    a = a.casefold()
    if prompt == 'Would you like to quit?' and a != 'no' and a != 'n':
        return True
    if a == 'y' or a == 'yes':
        return True
    if a == 'n' or a == 'no':
        return False
    if a == 'q' or a == 'quit':
        if YN('Would you like to quit?'):
            # critical(logger_instance.acc.accTime)
            quit()
    print('invalid input. Enter Y or N')
    out = YN(prompt)
    return out


@log
def weightedSelect(inputList):
    total = 0
    for item in inputList:
        total += item[0]
    key = random.uniform(0, total)
    for item in inputList:
        if key < item[0]:
            return item[1]
        key -= item[0]
    raise Exception('selection failed somehow')


def main():
    print('theres nothing here...')


if __name__ == '__main__':
    main()
