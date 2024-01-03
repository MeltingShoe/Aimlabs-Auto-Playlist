import yaml

def saveYAML(config):
    file = open("config.yaml", "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


def openYAML():

    with open("config.yaml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
