"""Environment configuration for Synapse IA."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load the .env file located in the SynapseIA project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "")
        self.secret_key = os.getenv("SECRET_KEY", "")
        self.neo4j_uri = os.getenv("NEO4J_URI", "")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model = os.getenv(
            "GROQ_MODEL", "llama-3.3-70b-versatile"
        ).strip()
        self.cors_origins = [
            origin.strip().rstrip("/")
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:4200"
            ).split(",")
            if origin.strip()
        ]


settings = Settings()
