from unittest.mock import MagicMock, patch

import pytest
from geopandas import GeoDataFrame

from ambipy_utils.postgres_handler import PostgresHandler


class TestPostgresHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        with (
            patch(
                "ambipy_utils.postgres_handler.psycopg2.connect"
            ) as mock_connect,
            patch(
                "ambipy_utils.postgres_handler.create_engine"
            ) as mock_create_engine,
        ):
            self.mock_conn = MagicMock()
            self.mock_cursor = MagicMock()
            mock_connect.return_value = self.mock_conn
            self.mock_conn.cursor.return_value.__enter__.return_value = (
                self.mock_cursor
            )

            self.mock_engine = MagicMock()
            mock_create_engine.return_value = self.mock_engine

            self.db_handler = PostgresHandler(
                database="test_db",
                user="user",
                password="pass",
                host="localhost",
                port=5432,
            )

            yield

    def test_commit(self):
        self.db_handler.commit()
        self.mock_conn.commit.assert_called_once()

    def test_rollback(self):
        self.db_handler.rollback()
        self.mock_conn.rollback.assert_called_once()

    def test_close(self):
        self.db_handler.close()
        self.mock_conn.close.assert_called_once()

    def test_truncate_table(self):
        self.db_handler.truncate_table("public", "my_table")
        self.mock_cursor.execute.assert_called_with(
            'TRUNCATE TABLE "public"."my_table"'
        )

    def test_reset_sequence(self):
        self.db_handler.reset_sequence("public", "my_table", "id")
        self.mock_cursor.execute.assert_called_with(
            'ALTER SEQUENCE "public"."my_table_id_seq" RESTART WITH 1'
        )

    def test_send_geodataframe(self):
        mock_gdf = MagicMock(spec=GeoDataFrame)

        self.db_handler.send_geodataframe(
            gdf=mock_gdf,
            table="test_table",
            schema="public",
            if_exists="append",
            chunksize=1000,
        )

        mock_gdf.to_postgis.assert_called_once_with(
            name="test_table",
            schema="public",
            con=self.mock_engine,
            if_exists="append",
            index=False,
            chunksize=1000,
        )

    def test_fetchall(self):
        self.mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        result = self.db_handler.fetchall("SELECT * FROM test")
        self.mock_cursor.execute.assert_called_with("SELECT * FROM test", None)
        assert result == [("row1",), ("row2",)]

    def test_fetchall_dict(self):
        mock_dict_cursor = MagicMock()
        mock_dict_cursor.fetchall.return_value = [{"id": 1}, {"id": 2}]
        self.mock_conn.cursor.return_value.__enter__.return_value = (
            mock_dict_cursor
        )

        result = self.db_handler.fetchall_dict("SELECT * FROM test")
        mock_dict_cursor.execute.assert_called_with("SELECT * FROM test", None)
        assert result == [{"id": 1}, {"id": 2}]

    def test_execute(self):
        self.db_handler.execute("DELETE FROM test WHERE id=%s", (1,))
        self.mock_cursor.execute.assert_called_with(
            "DELETE FROM test WHERE id=%s", (1,)
        )

    def test_executemany(self):
        self.db_handler.executemany(
            "INSERT INTO test VALUES (%s)", [(1,), (2,)]
        )
        self.mock_cursor.executemany.assert_called_with(
            "INSERT INTO test VALUES (%s)", [(1,), (2,)]
        )
