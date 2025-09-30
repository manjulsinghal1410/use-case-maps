"""
Centralized configuration management for the Databricks Use Case Plans app.
Database connection will be configured once user provides Lakebase connection details.
"""

import os
from pathlib import Path

# Try to load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # dotenv not installed, that's okay we'll use placeholder values
    pass

class Config:
    """Configuration class for Lakebase connection"""

    # Database connection settings (to be updated with actual values)
    LAKEBASE_HOST = os.getenv('LAKEBASE_HOST', 'placeholder-host')
    LAKEBASE_PORT = int(os.getenv('LAKEBASE_PORT', '5432'))
    LAKEBASE_DB_NAME = os.getenv('LAKEBASE_DB_NAME', 'placeholder-db')
    LAKEBASE_DB_USER = os.getenv('LAKEBASE_DB_USER', 'placeholder-user')
    LAKEBASE_DB_PASSWORD = os.getenv('LAKEBASE_DB_PASSWORD', 'placeholder-password')

    # Database Connection Settings
    DB_SSL_MODE = os.getenv('DB_SSL_MODE', 'require')

    # Application Settings
    APP_NAME = "Databricks Use Case Plans"
    APP_VERSION = "1.0.0"

    # Databricks Official Brand Colors (from brand.databricks.com)
    DATABRICKS_LAVA_600 = "#FF3621"        # Lava 600 (Primary brand color)
    DATABRICKS_NAVY_800 = "#0B2026"        # Navy 800 (Deep navy from brand site)
    DATABRICKS_OAT_MEDIUM = "#F9F7F4"      # Oat Medium (Brand background color)
    DATABRICKS_OAT_LIGHT = "#FFFFFF"       # Oat Light (White)
    DATABRICKS_WHITE = "#FFFFFF"           # Pure White
    DATABRICKS_ACCENT_ORANGE = "#FF6B35"   # Complementary orange
    DATABRICKS_GRAY = "#4A4A4A"            # Brand gray color

    # Multi-user settings
    DEFAULT_USERS = [
        "Manjul Singhal",
        "Dennis Clark",
        "Amelia Russell",
        "Matt Johnson",
        "Saket Patel"
    ]

    @classmethod
    def validate(cls):
        """Validate that we have the required credentials"""
        required_fields = [
            cls.LAKEBASE_HOST,
            cls.LAKEBASE_DB_NAME,
            cls.LAKEBASE_DB_USER,
            cls.LAKEBASE_DB_PASSWORD
        ]
        return all(field and field != "placeholder-host" and not field.startswith("placeholder")
                  for field in required_fields)

    @classmethod
    def get_connection_params(cls):
        """Get database connection parameters as a dictionary"""
        return {
            'host': cls.LAKEBASE_HOST,
            'port': cls.LAKEBASE_PORT,
            'dbname': cls.LAKEBASE_DB_NAME,
            'user': cls.LAKEBASE_DB_USER,
            'password': cls.LAKEBASE_DB_PASSWORD,
            'sslmode': cls.DB_SSL_MODE,
        }

    @classmethod
    def update_connection(cls, host, port, dbname, user, password, sslmode='require'):
        """Update connection parameters (for when user provides actual details)"""
        cls.LAKEBASE_HOST = host
        cls.LAKEBASE_PORT = port
        cls.LAKEBASE_DB_NAME = dbname
        cls.LAKEBASE_DB_USER = user
        cls.LAKEBASE_DB_PASSWORD = password
        cls.DB_SSL_MODE = sslmode

    @classmethod
    def print_config(cls):
        """Print current configuration (masks sensitive values)"""
        print("=== Databricks Use Case Plans Configuration ===")
        print(f"APP_NAME: {cls.APP_NAME}")
        print(f"APP_VERSION: {cls.APP_VERSION}")
        print(f"LAKEBASE_HOST: {cls.LAKEBASE_HOST}")
        print(f"LAKEBASE_PORT: {cls.LAKEBASE_PORT}")
        print(f"LAKEBASE_DB_NAME: {cls.LAKEBASE_DB_NAME}")
        print(f"LAKEBASE_DB_USER: {cls.LAKEBASE_DB_USER}")
        print(f"DB_SSL_MODE: {cls.DB_SSL_MODE}")
        print(f"LAKEBASE_DB_PASSWORD: {'*' * 20 if cls.LAKEBASE_DB_PASSWORD else 'Not Set'}")
        print(f"DATABASE_VALIDATED: {cls.validate()}")
        print("=" * 50)

# Create a singleton config instance
config = Config()