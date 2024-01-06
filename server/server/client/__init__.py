import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


class StashgresClient:
    def __init__(self) -> None:
        dbname = 'stashgres'
        user = 'postgres'
        password = 'postgres'
        port = '5454'
        host = 'localhost'

        self._stashgres_url = f'postgres://{user}:{password}@{host}:{port}/{dbname}'
        self._stashgres_kv = f'dbname={dbname} user={user} password={password} port={port} host={host}'

    def execute(self, query: str, values: list, fetch: str = 'all') -> None:
        with psycopg.connect(self._stashgres_kv) as conn:

            # Open a cursor to perform database operations
            with conn.cursor(row_factory=dict_row) as cur:

                # Pass data to fill a query placeholders and let Psycopg perform
                # the correct conversion without  SQL injections.
                if fetch == 'one':
                    _executed_values = cur.execute(query, values).fetchone()
                else:
                    _executed_values = cur.execute(query, values).fetchall()

                # Make the changes to the database persistent
                conn.commit()

        return _executed_values

    async def aexecute(self, query: str, values: list, fetch: str = 'all') -> None:
        # async with await psycopg.AsyncConnection.connect(
        #         "dbname=test user=postgres") as aconn:
        #     async with aconn.cursor() as acur:
        #         await acur.execute(
        #             "INSERT INTO test (num, data) VALUES (%s, %s)",
        #             (100, "abc'def"))
        #         await acur.execute("SELECT * FROM test")
        #         await acur.fetchone()
        #         # will return (1, 100, "abc'def")
        #         async for record in acur:
        #             print(record)

        async with await psycopg.AsyncConnection.connect(self._stashgres_kv) as aconn:

            # Open a cursor to perform database operations
            async with aconn.cursor(row_factory=dict_row) as acur:

                # Pass data to fill a query placeholders and let Psycopg perform
                # the correct conversion without  SQL injections.
                if fetch == 'one':
                    _executed_values = await acur.execute(query, values).fetchone()
                else:
                    _executed_values = await acur.execute(query, values).fetchall()

                # Make the changes to the database persistent
                aconn.commit()

        return _executed_values
