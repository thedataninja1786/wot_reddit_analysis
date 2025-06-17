import psycopg2
import pandas as pd
from typing import Tuple, List, Optional, Any


class DataLoader:
    def __init__(
        self, user: str, password: str, host: str, port: str, dbname: str
    ) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname

    def _connect(self) -> None:
        """Establishes connection to Postgres"""

        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )
        except Exception as e:
            print(
                f"{self.__class__.__name__} - {self._connect.__name__}: failed to connect "
                f"to: {self.dbname} - {self.host} on port {self.port}!"
            )
            print(e)
            raise

    def __repr__(self) -> str:
        return (
            f"Postgres(user='{self.user}', password='***', "
            f"host='{self.host}', port='{self.port}', dbname='{self.dbname}')"
        )

    def write_data(
        self,
        table_name: str,
        data_rows: List[Tuple[Any, ...]],
        column_names: List[str],
        write_method: str,
        upsert_on: Optional[List[str]] = None,
    ) -> None:
        """Writes data to a database table using the specified method (replace, append, upsert)."""

        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor = conn.cursor()

                    if write_method == "replace":
                        cursor.execute(f"DELETE FROM {table_name};")
                        conn.commit()
                        write_method = "append"  # append after replace

                    if write_method == "append":
                        insert_query = f"""
                            INSERT INTO {table_name} ({', '.join(column_names)})
                            VALUES ({', '.join(['%s'] * len(column_names))});
                        """
                        cursor.executemany(insert_query, data_rows)
                        conn.commit()

                    elif write_method == "upsert":
                        if upsert_on is None:
                            raise ValueError(
                                "upsert_on must be provided for upsert operations."
                            )

                        conflict_cols = ", ".join(upsert_on)
                        update_cols = [col for col in column_names if col not in upsert_on]
                        update_clause = ", ".join(
                            [
                                f"{col} = EXCLUDED.{col}"
                                for col in update_cols
                                if col != "processing_timestamp"
                            ]
                            + ["processing_timestamp = now()"]
                        )

                        upsert_query = f"""
                            INSERT INTO {table_name} ({', '.join(column_names)})
                            VALUES ({', '.join(['%s'] * len(column_names))})
                            ON CONFLICT ({conflict_cols})
                            DO UPDATE SET {update_clause};
                        """
                        cursor.executemany(upsert_query, data_rows)
                        conn.commit()

                    else:
                        raise NotImplementedError(f"{write_method} is not implemented!")

                    print(f"Row data successfully {write_method} on table {table_name}!")

        except Exception as e:
            print(
                f"{self.__class__.__name__} - {self.write_data.__name__}: an error "
                f"occurred while {write_method} data to the table '{table_name}': {e}"
            )
            raise

    def create_table(self, table_name: str, fields: dict) -> None:
        """Creates a table in the database with the specified name and fields."""

        try:
            columns = ", ".join([f"{col} {dtype}" for col, dtype in fields.items()])
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"

            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor = conn.cursor()
                    cursor.execute(create_query)
                    conn.commit()
                    print(f"Table '{table_name}' created successfully!")
        except Exception as e:
            print(
                f"{self.__class__.__name__} - {self.create_table.__name__}: an error "
                f"occurred while creating the table '{table_name}': {e}"
            )
            raise

    def drop_table(self, table_name: str) -> None:
        """Drops a table from the database if it exists."""

        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor = conn.cursor()
                    drop_query = f"DROP TABLE IF EXISTS {table_name}"
                    cursor.execute(drop_query)
                    conn.commit()
                    print("Table dropped successfuly!")
        except Exception as e:
            print(
                f"{self.__class__.__name__} - {self.drop_table.__name__}: an error "
                f"occurred while dropping the table: {e}"
            )
            raise

    def query_table(self, query: str) -> pd.DataFrame:
        try:
            with self._connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            print(
                f"{self.__class.__name__} - {self.query_table.__name__}: an error while querying:",
                e,
            )
            raise
