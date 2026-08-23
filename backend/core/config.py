from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):
    GITHUB_CLIENT_ID:str 
    GITHUB_CLIENT_SECRET:str
    GITHUB_REDIRECT_URI:str 
    DATABASE_URL:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    GROQ_API_KEY:str  
    GROQ_MODEL:str
    model_config = SettingsConfigDict(
        env_file=".env"
    )
settings = Settings()
