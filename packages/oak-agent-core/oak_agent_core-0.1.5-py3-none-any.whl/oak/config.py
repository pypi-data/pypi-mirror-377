# Configuration management
import os
import uuid
from pathlib import Path

# Get the base directory of the project
basedir = Path(__file__).resolve().parent.parent

class Config:
    # General Config
    SECRET_KEY = os.getenv('SECRET_KEY', str(uuid.uuid4()))
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    
    # Celery Config
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    
    # Database URI: SQLAlchemy configuration
    # Use an environment variable for the database URI in production.
    # Example for PostgreSQL: 'postgresql://user:password@host:port/dbname'
    # Example for SQLite (local dev): 'sqlite:///oakquant.db'

    # New: Flag to switch between SQLite and pgvector-enabled PostgreSQL locally
    # Set this to 'True' in your .env file or environment for local PostgreSQL with pgvector
    USE_PGVECTOR_DB = os.environ.get('USE_PGVECTOR_DB', 'False').lower() in ('true', '1', 't')

    if USE_PGVECTOR_DB:
        # Configuration for local PostgreSQL with pgvector
        # These values should match your docker-compose.yml for the 'db' service
        _pg_username = os.environ.get('POSTGRES_USER', 'oakquant_user')
        _pg_password = os.environ.get('POSTGRES_PASSWORD', 'oakquant_password')
        _pg_db = os.environ.get('POSTGRES_DB', 'oakquant_db')
        _pg_host = os.environ.get('POSTGRES_HOST', 'db') # 'db' is the service name in docker-compose
        _pg_port = os.environ.get('POSTGRES_PORT', '5432')
        SQLALCHEMY_DATABASE_URI = f"postgresql://{_pg_username}:{_pg_password}@{_pg_host}:{_pg_port}/{_pg_db}"
        print(f"INFO: Using PostgreSQL (pgvector-enabled) for DB: {SQLALCHEMY_DATABASE_URI.split('@')[-1]}")
    else:
        # Check for DigitalOcean's component-specific environment variables first (for production)
        DB_USERNAME = os.environ.get('DB_USERNAME')
        DB_PASSWORD = os.environ.get('DB_PASSWORD')
        DB_HOST = os.environ.get('DB_HOST')
        DB_PORT = os.environ.get('DB_PORT')
        DB_NAME = os.environ.get('DB_NAME')

        if all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
            # If all DigitalOcean variables are present, build the PostgreSQL connection string
            SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?connect_timeout=10&sslmode=require"
            print(f"INFO: Using DigitalOcean PostgreSQL for DB: {SQLALCHEMY_DATABASE_URI.split('@')[-1]}")
        else:
            # Otherwise, fall back to the local SQLite database for development
            db_path = basedir / 'db' / 'oakquant.db'
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
            print(f"INFO: Using SQLite for DB: {SQLALCHEMY_DATABASE_URI}")
        
    # A common "gotcha": Heroku/DigitalOcean use 'postgres://', but SQLAlchemy needs 'postgresql://'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Suppress SQLAlchemy track modifications warning
    
    # --- SQLAlchemy connection pooling options ---
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Checks if connections are alive before using.
        "pool_recycle": 1800,   # Recycles connections every 30 minutes.
    }

    # NEW: SQLAlchemy connection pooling settings for use with PgBouncer
    # These settings are crucial when using an external connection pooler like PgBouncer.
    # They tell SQLAlchemy to trust the external pooler and not manage its own extensive pool.
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE', '2')) # Keep a small pool in the app
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW', '0')) # Allow some overflow if needed
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', '30')) # Seconds to wait for a connection
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', '3600')) # Recycle connections after 1 hour (PgBouncer handles this better)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True, # Test connections for liveness
        'pool_use_lifo': True, # Use LIFO for better connection reuse
    }