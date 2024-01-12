from utils import openYAML, saveYAML, rawDB


def resetStats():
    config = openYAML('config.yaml')
    db = rawDB()
    data = db.readDB()
    last = data[-1]
    ID = last[0]
    config['resetPoint'] = ID
    saveYAML(config, 'config.yaml')


def main():
    resetStats()


if __name__ == '__main__':
    main()
