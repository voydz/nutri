.PHONY: setup run build clean lint lint-fix package smoke test check

.DEFAULT_GOAL := check

setup:
	uv venv
	uv sync --extra dev

run:
	uv run python -m nutricli

lint:
	uv run ruff check src/
	uv run ruff format --check src/

lint-fix:
	uv run ruff check --fix src/
	uv run ruff format src/

test:
	uv run pytest

check: lint test

build:
	uv run pyinstaller \
		--onefile \
		--name nutri \
		--target-arch arm64 \
		--additional-hooks-dir hooks \
		src/nutricli/__main__.py

package: build
	@set -e; \
	VERSION=$$(grep '^version' pyproject.toml | head -1 | cut -d'"' -f2); \
	echo "Packaging nutri v$$VERSION..."; \
	cd dist && \
	PKG="nutri-cli-$$VERSION-macos.tar.gz"; \
	tar -czf "$$PKG" nutri && \
	shasum -a 256 "$$PKG" | cut -d' ' -f1 > "$$PKG.sha256" && \
	echo "SHA256: $$(cat "$$PKG.sha256")"

smoke: build
	@set -e; \
	tmp_home="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp_home"' EXIT; \
	env -i PATH="/usr/bin:/bin:/usr/sbin:/sbin" HOME="$$tmp_home" \
		PYTHONNOUSERSITE=1 PYTHONPATH= PYTHONHOME= \
		VIRTUAL_ENV= CONDA_PREFIX= CONDA_DEFAULT_ENV= PIPENV_ACTIVE= \
		PYENV_VERSION= UV_PROJECT_ENV= \
		./dist/nutri --help

clean:
	rm -rf dist build __pycache__ src/nutricli/__pycache__
