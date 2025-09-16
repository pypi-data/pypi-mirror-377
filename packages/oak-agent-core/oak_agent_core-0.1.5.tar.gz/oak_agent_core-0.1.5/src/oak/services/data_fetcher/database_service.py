from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from oak.config import Config
from oak.services.data_fetcher.exceptions import DatabaseConnectionError

# We use create_engine outside of a function to have a shared engine instance
# for the application. The engine is a factory for connections.
_db_engine = None

def get_db_engine(db_uri=None):
    """
    Returns a shared, pre-configured SQLAlchemy engine instance.
    """
    global _db_engine
    if _db_engine is None:
        if db_uri is None:
            db_uri = Config.SQLALCHEMY_DATABASE_URI
        try:
            _db_engine = create_engine(
                db_uri,
                **Config.SQLALCHEMY_ENGINE_OPTIONS
            )
            # Test the connection to fail fast on startup
            with _db_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("INFO: SQLAlchemy engine created successfully.")
        except Exception as e:
            raise DatabaseConnectionError(f"Could not connect to the database: {e}")
    return _db_engine

def get_db_connection(db_uri=None):
    """
    Returns a single database connection from the engine's pool.
    """
    return get_db_engine(db_uri).connect()

def get_db_session(db_uri=None):
    """
    Returns a SQLAlchemy session for ORM operations.
    """
    Session = sessionmaker(bind=get_db_engine(db_uri))
    return Session()