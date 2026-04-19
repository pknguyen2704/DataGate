import sys
from sqlalchemy import create_engine, text
engine = create_engine("postgresql://admin:datagatepassword@localhost:5432/datagate")
with engine.connect() as conn:
    res = conn.execute(text("SELECT DISTINCT table_name FROM dg_observability_snapshots"))
    for row in res:
        print(f"Table in DB: {row[0]}")
