import json


def load_configs():
    configs = {}
    with open('configs/master_config.json') as json_data:
        configs = json.load(json_data)

    return configs
