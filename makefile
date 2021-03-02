.DEFAULT_GOAL := default_target

PROJECT_NAME := address-core
PYTHON_VERSION := 3.7.6
VENV_NAME := $(PROJECT_NAME)-$(PYTHON_VERSION)

# Code style
code-convention:
	flake8
	pycodestyle

# Remove useless files
.clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr reports/
	rm -fr .pytest_cache/

clean: .clean-build .clean-pyc .clean-test ## remove all build, test, coverage and Python artifacts

# Virtual Env
.create-venv:
	pyenv install -s $(PYTHON_VERSION)
	pyenv uninstall -f $(VENV_NAME)
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)

create-venv: .create-venv setup-dev

# Setup
.pip:
	pip install pip --upgrade

setup: .pip
	pip install -r requirements/base.txt

setup-dev: .pip
	pip install -r requirements/local.txt

setup-production: .pip
	pip install -r requirements/production.txt

# Test
test:
	pytest --cov-report=term-missing  --cov-report=html --cov=.