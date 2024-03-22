import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StashgresClient:
    def __init__(self) -> None:
        user = 'postgres'
        password = os.environ.get('POSTGRES_PASSWORD')
        host = os.environ.get('POSTGRES_HOST')
        port = os.environ.get('POSTGRES_PORT')
        dbname = 'stashgres'

        self.uri = f'postgres://{user}:{password}@{host}:{port}/{dbname}'
        self.kv = f'dbname={dbname} user={user} password={password} port={port} host={host}'


stashgres_client = StashgresClient()
