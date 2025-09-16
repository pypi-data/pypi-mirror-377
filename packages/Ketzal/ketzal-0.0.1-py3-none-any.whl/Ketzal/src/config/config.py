import os
from dotenv import dotenv_values

class Config:
    def __init__(self, env_file=".env"):
        self._load_env(env_file)
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", 5002))
        self.debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    def _load_env(self, env_file):
        if os.path.exists(env_file):
            for k, v in dotenv_values(env_file).items():
                if v is not None:
                    os.environ[k] = v
