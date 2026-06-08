.PHONY: up down build logs migrate seed test lint shell consumer clean

# ─── Docker Compose ───
up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

down-volumes:
	docker compose down -v

build:
	docker compose build

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend worker

logs-kafka:
	docker compose logs -f kafka

# ─── Django ───
migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

createsuperuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose exec backend python manage.py shell

# ─── Kafka Consumer ───
consumer:
	docker compose exec worker python manage.py run_consumer

# ─── Testing ───
test:
	docker compose exec backend python -m pytest -v

test-frontend:
	docker compose exec frontend npm test

lint:
	docker compose exec backend python -m ruff check .
	docker compose exec frontend npm run lint

# ─── Seed Data ───
seed:
	docker compose exec backend python manage.py seed_data

# ─── Cleanup ───
clean:
	docker compose down -v --remove-orphans
	docker system prune -f
