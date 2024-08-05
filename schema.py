import pandas as pd

from connector import set_connection
from sqlalchemy import text

schema_creation_query = """ 
    create schema course_prj;
"""
with set_connection() as ps:
    ps.execute(text(schema_creation_query))
    ps.commit()
