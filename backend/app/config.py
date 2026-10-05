from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "LowTicket Ads Studio"
    database_url: str = "sqlite:///./lowticket_ads.db"
    frontend_origin: str = "http://localhost:5173"
    daily_budget_multiplier: int = 3

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            frontend_origin=os.getenv("FRONTEND_ORIGIN", cls.frontend_origin),
            daily_budget_multiplier=int(os.getenv("DAILY_BUDGET_MULTIPLIER", "3")),
        )


settings = Settings.from_env()
