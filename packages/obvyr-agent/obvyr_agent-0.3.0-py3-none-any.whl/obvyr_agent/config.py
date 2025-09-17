"""
Configuration for Obvyr Agent.

The BaseSettings object will attempt to replace any properties
from environment variables, allowing environmental overrides.
"""

import secrets
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_AGENT_URL = "https://api.obvyr.com"


class AgentSettings(BaseModel):
    """Configuration for an Obvyr Agent."""

    API_KEY: str
    API_URL: str = DEFAULT_AGENT_URL
    ATTACHMENT_PATH: str | None = None
    ATTACHMENT_MAX_AGE_SECONDS: int = 10
    TIMEOUT: float = 10.0
    VERIFY_SSL: bool = True
    TAGS: list[str] = Field(default_factory=list)

    @field_validator("TAGS", mode="before")
    @classmethod
    def parse_tags(cls, value: str | list[str]) -> list[str]:
        """Parse tags from comma-separated string or return list as-is."""
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return value or []


class Settings(BaseSettings):
    """Configuration and settings for the Obvyr Agent."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OBVYR_",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="ignore",
        populate_by_name=True,
    )

    SECRET_KEY: str = secrets.token_urlsafe(32)
    AGENTS: Dict[str, AgentSettings] = Field(default_factory=dict)

    def get_agent(self, agent_name: str | None = None) -> AgentSettings:
        """Return settings for the specified agent or default to DEFAULT agent."""
        if agent_name:
            active_agent = agent_name.strip().upper()
        else:
            active_agent = "DEFAULT"

        if active_agent not in self.AGENTS:
            raise ValueError(
                f"Agent '{active_agent}' not found in configuration."
            )
        agent = self.AGENTS[active_agent]

        return agent

    def list_agents(self) -> list:
        """Return a list of available agents."""
        return list(self.AGENTS.keys())

    def show_config(self, agent_name: str | None = None) -> dict:
        """Show active agent's settings (excluding API keys)."""
        active_agent = self.get_agent(agent_name)
        return {
            k.upper(): v
            for k, v in active_agent.model_dump().items()
            if "KEY" not in k.upper()
        }


def get_settings() -> Settings:
    """Return the current settings."""
    load_dotenv(".env", override=True)

    return Settings()
