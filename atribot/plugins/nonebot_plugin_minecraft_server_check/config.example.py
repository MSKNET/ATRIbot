from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    MC_API_SERVER: str = "https://api.mcsrvstat.us/2/"
    MC_API_SERVER_BEDROCK: str = "https://api.mcsrvstat.us/bedrock/2/"
    MC_SERVERS: dict = {
        # "addr": "desc",
    }
    MC_BEDROCK_SERVERS: dict = {
        # "addr": "desc",
    }

    class Config:
        extra = "ignore"
