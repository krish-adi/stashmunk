from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.client import StashgresClient

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
        dbname = 'stashgres'
        user = 'postgres'
        password = 'postgres'
        port = '5454'
        host = 'localhost'

        self.uri = f'postgres://{user}:{password}@{host}:{port}/{dbname}'
        self.kv = f'dbname={dbname} user={user} password={password} port={port} host={host}'


stashgres_client = StashgresClient()
