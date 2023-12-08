include .env
export

.ONESHELL:

.PHONY: db
db:
	docker run -d --name stashmunk-db -p 5432:${POSTGRES_PORT} -e POSTGRES_DB=${POSTGRES_DB} \
	-e POSTGRES_USER=${POSTGRES_USER} -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	-v ${PWD}/database/persist:/var/lib/postgresql/data postgres