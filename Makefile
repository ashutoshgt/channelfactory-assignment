# Build the Docker Compose service
build:
	docker compose build api

# Run the Docker Compose service
run:
	docker compose up api

# Build and run the Docker Compose service
build-run:
	make build
	make run

stop:
	docker compose down --remove-orphans --volumes

run-unit-tests:
	docker compose run api pytest --cov=geo geo/tests/unit

run-integration-tests:
	docker compose run api pytest --cov=geo geo/tests/integration

run-bash:
	docker compose run api bash

run-migrations:
	docker compose run api python manage.py migrate

.PHONY: run stop build build-run run-bash run-migrations run-unit-tests run-integration-tests
