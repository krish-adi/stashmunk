from fastapi import Request
import json
from server import app

# app.include_router(token_router)


@app.get("/", tags=["health-check"],)
async def root(request: Request):
    params = request.query_params._dict

    if params:
        return f"Hey there folks! Here are the query Parameters :: {json.dumps(params)}"

    return "Hey there folks. How ya'll doing today?"


@app.on_event("startup")
async def startup_event():
    print('Connecting to creds database...')
    print('Connected to creds database...')


@app.on_event("shutdown")
async def shutdown_event():
    print('Disconnecting from creds database...')
    print('Disconnected from creds database...')
