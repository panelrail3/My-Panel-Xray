from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "CHANGE-ME"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me"
    DATABASE_URL: str = "sqlite:////data/panel.db"
    XRAY_PATH: str = "/usr/local/bin/xray"
    XRAY_CONFIG: str = "/data/xray/config.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
