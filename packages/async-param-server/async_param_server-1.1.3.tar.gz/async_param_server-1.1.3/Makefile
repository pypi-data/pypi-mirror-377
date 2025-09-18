.PHONY : install test clean build docker-build-and-publish docker-run stop server server-bg

install:
	uv tool install -e .
	uv tool update-shell

# Testing
test:
	uv sync --extra dev
	uv run pytest tests/ -v

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	uv build

make publish: build
	uv publish


docker-run:
	docker compose -f docker-compose.yml up --build -d param-server

stop:
	docker compose -f docker-compose.yml down

.ONESHELL:
docker-build-and-publish:
	export $$(grep -v '^#' .env | grep "GITLAB" | xargs -d '\n')
	export VERSION=$$(cat ./pyproject.toml | grep "version" | grep -oh "[0-9]\+.[0-9]\+.[0-9]\+")
	echo "$$GITLAB_DOCKER_TOKEN" | docker login gitlab.isdd.sk:4567 -u matus.zelenak@isdd.sk --password-stdin
	docker build -t "gitlab.isdd.sk:4567/hollen/k2/param-server:$$VERSION" -t "hollen/param-server:$$VERSION" .
	docker push "gitlab.isdd.sk:4567/hollen/k2/param-server:$$VERSION"

# Local development
server:
	uv run python -m param_server.server --config examples/config/params.yml --log-level DEBUG --host 0.0.0.0

server-bg:
	uv run python -m param_server.server --config examples/config/params.yml --log-level INFO --host 0.0.0.0 &
