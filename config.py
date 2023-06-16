import yaml


class Config(dict):

    def __init__(self):
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
        super().__init__(data)


config = Config()
