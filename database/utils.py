from sqlalchemy import text
from database.connection import engine
from database.models import Base


def clear_data():
    """Delete data from tables"""
    names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {names} RESTART IDENTITY CASCADE"))
    print("Deleted every record")



def delete_tables():
    """Drop every table (and its sequences)"""
    Base.metadata.drop_all(engine)
    print("Dropped every table")
