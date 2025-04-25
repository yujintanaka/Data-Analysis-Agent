from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from contextlib import contextmanager
from .state import AgentState

def get_db_engine(state: AgentState) -> Engine:
    """
    Creates and returns an SQLAlchemy engine based on the database configuration in the state.
    The engine is created with the appropriate database type and URI from the state.
    """
    if "db_type" not in state["input_data"] or "db_uri" not in state["input_data"]:
        raise ValueError("Database configuration (db_type and db_uri) must be provided in the state")
    
    return create_engine(state["input_data"]["db_uri"])

@contextmanager
def get_db_session(state: AgentState):
    """
    Provides a database session context manager that automatically handles session cleanup.
    Usage:
        with get_db_session(state) as session:
            # Use session here
    """
    engine = get_db_engine(state)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

@contextmanager
def get_db_connection(state: AgentState):
    """
    Provides a database connection context manager that automatically handles connection cleanup.
    Usage:
        with get_db_connection(state) as connection:
            # Use connection here
    """
    engine = get_db_engine(state)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close() 