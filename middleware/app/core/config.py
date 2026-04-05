from functools import lru_cache
from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    app_version: str = "0.0.0"
    
    model_config = {'env_file':'.env'}
    
    
@lru_cache(maxsize=128)
def get_settings() -> Settings:
    return Settings()