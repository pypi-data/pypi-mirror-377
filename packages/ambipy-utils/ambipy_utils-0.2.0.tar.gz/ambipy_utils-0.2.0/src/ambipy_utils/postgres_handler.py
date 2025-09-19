from typing import Optional

import psycopg2
import psycopg2.extras
from geopandas import GeoDataFrame
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class PostgresHandler:
    def __init__(
        self,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 5432,
    ):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self.conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.engine: Engine = create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def truncate_table(self, schema: str, table: str):
        with self.conn.cursor() as cur:
            cur.execute(f'TRUNCATE TABLE "{schema}"."{table}"')

    def reset_sequence(self, schema: str, table: str, id_column: str):
        with self.conn.cursor() as cur:
            cur.execute(
                (
                    f'ALTER SEQUENCE "{schema}"."{table}_{id_column}_seq" '
                    f"RESTART WITH 1"
                )
            )

    def send_geodataframe(
        self,
        gdf: GeoDataFrame,
        table: str,
        schema: str,
        if_exists: str = "append",
        chunksize: int = 5000,
    ):
        gdf.to_postgis(
            name=table,
            schema=schema,
            con=self.engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
        )

    def fetchall(
        self, query: str, params: Optional[dict] = None
    ) -> list[tuple]:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def fetchall_dict(
        self, query: str, params: Optional[dict] = None
    ) -> list[dict]:
        with self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query: str, params: Optional[dict | tuple] = None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)

    def executemany(self, query: str, data: list[tuple]):
        with self.conn.cursor() as cur:
            cur.executemany(query, data)
