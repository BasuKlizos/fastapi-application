import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    MONGO_URI: str = os.getenv("MONGO_URI")
    ALGORITHM: str = os.getenv("ALGORITHM")
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")


settings = Settings()
