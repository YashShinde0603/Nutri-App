from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str
    FDC_API_KEY: str

    # FastAPI / run
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # JWT / Auth
    SECRET_KEY: str = "changeme_replacethis_with_a_long_random_secret_please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"


settings = Settings()
