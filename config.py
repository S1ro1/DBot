import yaml
import os

class Config(dict):

    def __init__(self):
        keys = ["bot_token", "server_id", "semester_message", "bot_channel"]
        data = {}
        try:
            with open("config.yaml", "r") as f:
                data = yaml.safe_load(f)
        except:
            for key in keys:
                if key not in os.environ:
                    raise Exception(f"Missing environment variable {key}")
                val = os.environ[key]

                try:
                    val = int(val)
                except:
                    pass

                data[key] = val
                

        super().__init__(data)


config = Config()
