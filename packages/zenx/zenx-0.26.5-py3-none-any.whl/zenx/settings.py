from typing import List, Literal, Self
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "DEBUG"

    SESSION_BACKEND: str = "memory"
    SESSION_POOL_SIZE: int = 1
    SESSION_AGE: int = 900 # 15 minutes
    SESSION_BLUEPRINT_REDIS_KEY: str = "solver:spider"
    ACCESS_DENIAL_STATUS_CODES: List[int] = [401, 403, 429]

    CONCURRENCY: int = 1
    TASK_INTERVAL_SECONDS: float = 1.0
    START_OFFSET_SECONDS: float = 60.0

    MAX_SCRAPE_DELAY: float = 0.0 # disabled

    DB_TYPE: Literal["memory", "redis", "sqlite"] = "memory"
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_HOST: str | None = "localhost"
    DB_PORT: int | None = 6379
    DB_PATH: str | None = ".zenx/data.db"
    DQ_MAX_SIZE: int = 1000  # max size of the deque for memory database
    REDIS_RECORD_EXPIRY_SECONDS: int = 3456000 # 40 days (40*24*60*60)

    PROXY: str | None = None
    PROXY_SERVER: str | None = None
    PROXY_USER: str | None = None
    PROXY_PASS: str | None = None

    SYNOPTIC_GRPC_SERVER_URI: str = "ingress.opticfeeds.com"
    SYNOPTIC_GRPC_TOKEN: str | None = None
    SYNOPTIC_GRPC_ID: str | None = None
    # enterprise
    SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI: str | None = "us-east-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI: str | None = "eu-central-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI: str | None = "eu-west-2.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI: str | None = "us-east-1-chi-2a.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI: str | None = "us-east-1-nyc-2a.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI: str | None = "ap-northeast-1.enterprise.synoptic.com:50051"
    SYNOPTIC_ENTERPRISE_GRPC_TOKEN: str | None = None
    SYNOPTIC_ENTERPRISE_GRPC_ID: str | None = None

    SYNOPTIC_DISCORD_WEBHOOK: str | None = None

    SYNOPTIC_WS_API_KEY: str | None = None
    SYNOPTIC_WS_STREAM_ID: str | None = None
    SYNOPTIC_FREE_WS_API_KEY: str | None = None
    SYNOPTIC_FREE_WS_STREAM_ID: str | None = None

    MONITOR_ITXP_SOCKET_PATH: str | None = "/tmp/itxpmonitor.sock"
    MONITOR_ITXP_TRIGGER_STATUS_CODE: int | None = 200
    MONITORING_ENABLED: bool = False

    def __getattr__(self, name):
        if self.model_extra and name in self.model_extra:
            return self.model_extra[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    model_config = SettingsConfigDict(env_file=find_dotenv(".env"), extra="allow", case_sensitive=True)

    @model_validator(mode="after")
    def model_created(self) -> Self:
        if not self.PROXY:
            if self.PROXY_SERVER and self.PROXY_USER and self.PROXY_PASS:
                self.PROXY = f"http://{self.PROXY_USER}:{self.PROXY_PASS}@{self.PROXY_SERVER}"

        if self.APP_ENV == "dev":
            self.START_OFFSET_SECONDS = 10.0 # can cause issues with the scheduler beacuse scheduler starts at the beginning of the minute, min 60 seconds
            self.DB_TYPE = "memory"
        return self

settings = Settings()
settings.model_export()