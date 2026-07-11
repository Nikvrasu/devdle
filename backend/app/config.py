from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env.

    DATABASE_URL and JWT_SECRET are required: if either is missing the app
    must fail loudly at startup rather than fall back to a silent default
    (a missing secret would make JWT signatures untrustworthy).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET: str
    FRONTEND_ORIGIN: str

    def model_post_init(self, __context) -> None:
        missing = [
            name
            for name in ("DATABASE_URL", "JWT_SECRET")
            if not getattr(self, name)
        ]
        if missing:
            raise RuntimeError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Set them in the environment or a .env file before starting the app."
            )


settings = Settings()
