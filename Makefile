up:
	docker compose up -d --build

down:
	docker compose down

test:
	docker compose -f tests/functional/docker-compose.yml up --build

test_down:
	docker compose -f tests/functional/docker-compose.yml down
