.PHONY: check clean-pycache distclean black mypy test format ruff fix
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
PROJECT_DIRS = services/agent
# IGNORE_PATH = --ignore apple_synthia/nlx/integration_tests

install:
	uv lock
	uv venv
	uv sync
	source .venv/bin/activate

check: ruff mypy

ruff:
	@echo "============================== Linting and Formatting check ==================="
	ruff format --check $(PROJECT_DIRS) 
	ruff check $(PROJECT_DIRS)

fix: format
	ruff check --fix $(PROJECT_DIRS)

mypy:
	@echo "============================== Type check ========================="
	mypy 

test:
	cd $(PROJECT_DIRS); echo "Running pytest"; \
	uv run py.test -vv $(IGNORE_PATH) -W ignore

coverage:
	@echo "============================== Tests =============================="
	py.test -vv --cov --junitxml=.out/test_results.xml --cov-report "xml:.out/coverage.xml" $(IGNORE_PATH)
	@echo " => Open HTML coverage report in browser: .out/htmlcov/index.html"

format:
	ruff format $(PROJECT_DIRS) 

requirements:
	uv export --no-hashes --no-dev > requirements.txt
	uv export --no-hashes > requirements-test.txt

clean-pycache:
	find . -type d -name '__pycache__' -print0 | xargs -0 -I {} /bin/rm -rf "{}"

distclean: clean-pycache
	rm -rf dist

badges:
	make coverage
	genbadge tests -i .out/test_results.xml -o .html/badges/tests-badge.svg
	genbadge coverage -i .out/coverage.xml -o .html/badges/coverage-badge.svg
