from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    GROUP_ID: list = []
    RATE: float = 1/96

    class Config:
        extra = "ignore"
