include ../.env

# Usage: >>> make {command}

.ONESHELL:

.PHONY: server
server:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) POSTGRES_HOST=$(POSTGRES_HOST) POSTGRES_PORT=$(POSTGRES_PORT) \
	uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: parser
parser:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) POSTGRES_HOST=$(POSTGRES_HOST) POSTGRES_PORT=$(POSTGRES_PORT) \
	uvicorn server.worker_parser:app --reload --host 0.0.0.0 --port 8001