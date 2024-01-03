import yaml

def saveYAML(config,path="config.yaml"):
    file = open(path, "w")
    yaml.dump(config, file)
    file.close()
    print("YAML file saved.")


def openYAML(path="config.yaml"):

    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)