from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):
    GITHUB_CLIENT_ID:str 
    GITHUB_CLIENT_SECRET:str
    GITHUB_REDIRECT_URI:str 
    model_config = SettingsConfigDict(
        env_file=".env"
    )
settings = Settings()
