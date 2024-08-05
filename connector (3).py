from sqlalchemy import create_engine

db_string = 'postgresql+psycopg2://postgres:aziz22@localhost:5432/postgres'

def set_connection():
    engine = create_engine(db_string)
    return engine.connect()
