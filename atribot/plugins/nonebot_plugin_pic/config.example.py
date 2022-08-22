from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    DRIVE_URL: str = ""      # "GDIndex URL"
    DRIVE_PARAMS: dict = {}  # {"rootId": ""}

    class Config:
        extra = "ignore"
