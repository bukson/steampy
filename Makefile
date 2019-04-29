.PHONY: clean
clean:
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@rm -rf build dist .coverage MANIFEST

.PHONY: lint-flake8
flake8:
	@python3 flake8 coub_api tests

.PHONY: lint-isort
isort:
	@python3 run isort -rc --diff steampy example test

.PHONY: lint-mypy
lint-mypy:
	@python3 -m mypy --ignore-missing-imports steampy

.PHONY: lint-black
lint-black:
	@python3 -m black --diff --check .

.PHONY: lint
lint: lint-isort lint-flake8 lint-black lint-mypy

.PHONY: fmt
fmt:
	@python3 -m black . && isort -rc steampy examples test