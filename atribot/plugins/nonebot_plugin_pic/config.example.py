from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    DRIVE_URL: str = ""      # "GDIndex URL"
    DRIVE_PARAMS: dict = {}  # {"rootId": ""}
    GROUP_ID: list = []
    RATE: float = 1/256

    class Config:
        extra = "ignore"
