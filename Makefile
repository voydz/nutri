.PHONY: setup run build clean lint lint-fix package smoke test check

.DEFAULT_GOAL := check

PYTHON_VERSION ?= 3.11

# Platform detection: PyInstaller cannot cross-compile, so every artifact is
# named after the host it was built on.
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Darwin)
	OS := macos
	# --target-arch is a macOS-only flag.
	PYI_PLATFORM_FLAGS := --target-arch arm64
else
	OS := linux
	PYI_PLATFORM_FLAGS :=
endif

ifeq ($(UNAME_M),x86_64)
	ARCH := x86_64
else
	ARCH := arm64
endif

SHA256 := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo "shasum -a 256")

VERSION ?= $(shell grep '^version' pyproject.toml | head -1 | cut -d'"' -f2)

setup:
	uv venv --python $(PYTHON_VERSION)
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
		$(PYI_PLATFORM_FLAGS) \
		--additional-hooks-dir hooks \
		src/nutricli/__main__.py

package: build
	@set -e; \
	echo "Packaging nutri v$(VERSION) for $(OS)-$(ARCH)..."; \
	cd dist && \
	PKG="nutri-cli-$(VERSION)-$(OS)-$(ARCH).tar.gz"; \
	tar -czf "$$PKG" nutri && \
	$(SHA256) "$$PKG" | cut -d' ' -f1 > "$$PKG.sha256" && \
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
