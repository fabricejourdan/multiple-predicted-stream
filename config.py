import sys
import os
import json
import yaml


class Config:

    def __init__(self, config_file_path=None):
        if config_file_path is None:
            print("Class 'Config' - 'config_file_path' must be defined")
            sys.exit(0)
        self.config_file_path = config_file_path
        if not os.path.isfile(self.config_file_path):
            print("Class 'Config' - File does not exist - config_file_path:" + str(self.config_file_path))
            sys.exit(0)
        components = config_file_path.split('.')
        extension = components[len(components) - 1].lower()
        self.config = None
        if extension in ['json']:
            with open(config_file_path, 'r') as config_file:
                try:
                    self.config = json.loads(config_file.read())
                except Exception as e:
                    print("Class 'Config' - Cannot load json file - config_file_path:" + str(
                        self.config_file_path) + " - error:" + str(e))
                    sys.exit(0)
        elif extension in ['yaml', 'yml']:
            with open(config_file_path, 'r') as config_file:
                self.config = yaml.safe_load(config_file)
                if not isinstance(self.config, dict):
                    print("Class 'Config' - Cannot load yaml file - config_file_path:" + str(
                        self.config_file_path))
                    sys.exit(0)
        else:
            print("Class 'Config' - extension not allowed - config_file_path:" + str(self.config_file_path))
            sys.exit(0)

    def get_config(self):
        return self.config


if __name__ == "__main__":
    config_file_path = 'config.json'
    cfg = Config(config_file_path)
    print(cfg.get_config())
