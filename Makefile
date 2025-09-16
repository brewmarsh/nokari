.PHONY: up build test coverage lint format security type-check all-checks clean
install

install:
        pip install --upgrade pip
        pip install -r requirements-dev.txt

up:
        docker compose up -d

build:
        docker compose build --no-cache

clean:
        docker compose down -v --remove-orphans
        find . -type f -name "*.pyc" -delete
        find . -type d -name "__pycache__" -exec rm -r {} +

test:
        docker compose run --rm web python -m unittest discover tests

coverage:
        docker compose run --rm web coverage run -m unittest discover tests
        docker compose run --rm web coverage report -m

lint:
        docker compose run --rm web ruff check --fix .

format:
        docker compose run --rm web ruff format .

security:
        docker compose run --rm web bandit -r .

type-check:
        docker compose run --rm web mypy .

# This target now runs the checks inside a new container for consistency with CI
all-checks:
        docker compose run --rm web ruff check .
        docker compose run --rm web bandit -r .
        docker compose run --rm web mypy .
        docker compose run --rm web coverage run -m unittest discover tests
