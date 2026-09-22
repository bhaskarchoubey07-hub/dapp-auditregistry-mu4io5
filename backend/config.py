"""
AuditRegistry - Backend Environment Configuration & Validation
Handles secure server-side settings, validation, and secret masking.
"""

import os
import re
from typing import Optional, List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # Networking
    PORT: int = Field(default=8000)
    ENVIRONMENT: str = Field(default="development")
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None)
    
    # Security
    JWT_SECRET: str = Field(default="auditregistry-enterprise-insecure-dev-secret-do-not-use-in-prod")
    JWT_ALGORITHM: str = Field(default="HS256")
    
    # AI Microservice
    AI_SERVICE_URL: str = Field(default="http://localhost:8000")
    ML_CONTAMINATION_RATE: float = Field(default=0.08)
    
    # Blockchain
    BLOCKCHAIN_RPC_URL: str = Field(default="https://rpc.sepolia.org")
    CONTRACT_ADDRESS: str = Field(default="0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8")
    CHAIN_ID: int = Field(default=11155111)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def has_postgres(self) -> bool:
        return bool(self.DATABASE_URL and not "user:password" in self.DATABASE_URL and not "placeholder" in self.DATABASE_URL)

    @property
    def has_supabase_api(self) -> bool:
        return bool(
            self.SUPABASE_URL 
            and self.SUPABASE_SERVICE_ROLE_KEY 
            and not "your-project-id" in self.SUPABASE_URL
            and not "placeholder" in self.SUPABASE_SERVICE_ROLE_KEY
        )

    def mask_secret(self, secret: Optional[str]) -> str:
        if not secret:
            return "NOT_SET"
        if len(secret) <= 8:
            return "********"
        return f"{secret[:4]}...{secret[-4:]}"

    def get_public_summary(self) -> dict:
        return {
            "environment": self.ENVIRONMENT,
            "port": self.PORT,
            "frontendUrl": self.FRONTEND_URL,
            "hasPostgres": self.has_postgres,
            "hasSupabaseApi": self.has_supabase_api,
            "databaseConfigured": bool(self.DATABASE_URL),
            "contractAddress": self.CONTRACT_ADDRESS,
            "chainId": self.CHAIN_ID,
            "blockchainRpc": self.BLOCKCHAIN_RPC_URL,
            "contaminationRate": self.ML_CONTAMINATION_RATE
        }

def load_settings() -> Settings:
    from dotenv import load_dotenv
    # Load .env if present
    load_dotenv()
    
    port_val = os.getenv("PORT", "8000")
    try:
        port_int = int(port_val)
    except ValueError:
        port_int = 8000

    chain_val = os.getenv("CHAIN_ID", "11155111")
    try:
        chain_int = int(chain_val)
    except ValueError:
        chain_int = 11155111

    contam_val = os.getenv("ML_CONTAMINATION_RATE", "0.08")
    try:
        contam_float = float(contam_val)
    except ValueError:
        contam_float = 0.08

    return Settings(
        PORT=port_int,
        ENVIRONMENT=os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "development")),
        FRONTEND_URL=os.getenv("FRONTEND_URL", "http://localhost:5173"),
        DATABASE_URL=os.getenv("DATABASE_URL"),
        SUPABASE_URL=os.getenv("SUPABASE_URL"),
        SUPABASE_SERVICE_ROLE_KEY=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        JWT_SECRET=os.getenv("JWT_SECRET", "auditregistry-enterprise-insecure-dev-secret-do-not-use-in-prod"),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        AI_SERVICE_URL=os.getenv("AI_SERVICE_URL", "http://localhost:8000"),
        ML_CONTAMINATION_RATE=contam_float,
        BLOCKCHAIN_RPC_URL=os.getenv("BLOCKCHAIN_RPC_URL", "https://rpc.sepolia.org"),
        CONTRACT_ADDRESS=os.getenv("CONTRACT_ADDRESS", "0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8"),
        CHAIN_ID=chain_int
    )

settings = load_settings()
