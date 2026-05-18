import os
from pathlib import Path

import environ
from dotenv import load_dotenv


def _load_env_files():
    load_dotenv(".env")
    app_env = os.getenv("APP_ENV")
    if app_env:
        load_dotenv(f".env.{app_env}")
    load_dotenv(".env.local", override=True)


_load_env_files()


@environ.config(prefix="")
class Config:
    debug: bool = environ.bool_var(default=False, name="DEBUG")
    found_offers_file: Path = environ.var(default="data/found_offers.txt", name="FOUND_OFFERS_FILE", converter=Path)
    refresh_interval_minutes: int = environ.var(default=30, name="REFRESH_INTERVAL_MINUTES", converter=int)
    search_queries: list[str] = environ.var(
        default="golf 5 diely,golf 5 nd,golf 5 blatnik,golf 5 naraznik,golf 5 svetlo,golf 5 la7w",
        name="SEARCH_QUERIES",
        converter=lambda x: [q.strip() for q in x.split(",") if q.strip()],
    )

    @environ.config
    class Discord:
        token: str = environ.var(name="DISCORD_TOKEN")
        channel_id: int = environ.var(name="DISCORD_CHANNEL_ID", converter=int)

    discord: Discord = environ.group(Discord)


config = environ.to_config(Config)
