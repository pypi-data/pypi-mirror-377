from __future__ import annotations

from pathlib import Path

import dotenv
import os
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class Settings(BaseModel):
    bb_username: str = Field(default_factory=lambda: os.getenv("USERNAME", "demo"))
    bb_password: str = Field(default_factory=lambda: os.getenv("PASSWORD", "demo"))
    bb_base_url: str = Field(default_factory=lambda: os.getenv("BB_BASE_URL", "https://bb.cuhk.edu.cn"))

    cache_dir: Path = Field(default_factory=lambda: Path(os.getenv("BB_MCP_CACHE_DIR", Path.home() / ".bb_mcp")))
    @property
    def cache_file(self) -> Path:
        return self.cache_dir / "bb_mcp_cache.json"


settings = Settings()
