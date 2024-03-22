include .env
export

.ONESHELL:

.PHONY: stashgres
stashgres:
	docker run -d --name stashgres-db -p ${POSTGRES_PORT}:5432 -e POSTGRES_DB=stashgres \
	-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} stashgres:0 \

# -v ${PWD}/database/persist:/var/lib/postgresql/data

.PHONY: build
build:
	docker build -t stashgres:0 ./stashgres