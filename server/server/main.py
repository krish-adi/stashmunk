from fastapi import Request
import json
from server import app
from server.routers.stashes import router as stashes_router
from server.routers.knowledge import router as knowledge_router


app.include_router(stashes_router)
app.include_router(knowledge_router)


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
