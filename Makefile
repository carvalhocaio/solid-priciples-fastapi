run:
	uvicorn main:app --reload

lint:
	ruff check . && ruff check . --diff

format:
	ruff check . --fix && ruff format .

# Test commands
test:
	pytest

test-unit:
	pytest tests/unit -v -m unit

test-integration:
	pytest tests/integration -v -m integration

test-e2e:
	pytest tests/e2e -v -m e2e

test-cov:
	pytest --cov=app --cov-report=term-missing --cov-report=html

test-cov-unit:
	pytest tests/unit -v -m unit --cov=app --cov-report=term-missing

test-cov-integration:
	pytest tests/integration -v -m integration --cov=app --cov-report=term-missing

test-cov-e2e:
	pytest tests/e2e -v -m e2e --cov=app --cov-report=term-missing

test-watch:
	ptw -- -v

test-failed:
	pytest --lf -v

test-verbose:
	pytest -vv -s

coverage-report:
	pytest --cov=app --cov-report=html && open htmlcov/index.html

# Install test dependencies
install-test:
	uv sync --extra test

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
