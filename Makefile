# Run the Docker Compose service
run:
	docker-compose up -d

build:
	docker-compose build

# Stop the Docker Compose service
stop:
	docker-compose down

# Run tests for the Docker Compose service
test:
	docker-compose run api pytest

.PHONY: run stop test