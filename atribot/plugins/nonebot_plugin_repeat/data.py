import yaml
from pathlib import Path


class Data:
    __path: Path

    def __init__(self, path: Path = Path() / "data" / "repeat" / "config.yml"):
        self.__path = path
        self.__load()

    def __load(self):
        loaded_data = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
        if loaded_data:
            self.__dict__.update(loaded_data)
