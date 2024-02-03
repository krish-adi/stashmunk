include .env
export

.ONESHELL:

.PHONY: stashgres
stashgres:
	docker run -d --name stashgres-db -p ${POSTGRES_PORT}:5432 -e POSTGRES_DB=stashgres \
	-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	stashgres:0

.PHONY: build
build:
	docker build -t stashgres:0 ./stashgres

.PHONY: postgres
postgres:
	docker run -d --name stashmunk-db -p 5432:${POSTGRES_PORT} -e POSTGRES_DB=postgres \
	-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	-v ${PWD}/database/persist:/var/lib/postgresql/data postgres