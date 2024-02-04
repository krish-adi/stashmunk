import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from server.workers.parser import router as parser_router

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


app.include_router(parser_router)


@app.get("/", tags=["health-check"],)
async def root(request: Request):
    params = request.query_params._dict

    if params:
        return f"Hey there folks! Here are the query Parameters :: {json.dumps(params)}"

    return "Hey there folks. How ya'll doing today?"


@app.on_event("startup")
async def startup_event():
    print('Starting up...')
    print('Start up complete.')


@app.on_event("shutdown")
async def shutdown_event():
    print('Shutting down...')
    print('Shut down complete.')
