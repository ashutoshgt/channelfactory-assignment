# Build the Docker Compose service
build:
	docker-compose build api

# Run the Docker Compose service
run:
	docker-compose up api

# Build and run the Docker Compose service
build-run:
	make build
	make run

# Stop the Docker Compose service
stop:
	docker-compose down --remove-orphans --volumes

# Run tests for the Docker Compose service
test:
	docker-compose run api pytest

.PHONY: run stop test build build-run