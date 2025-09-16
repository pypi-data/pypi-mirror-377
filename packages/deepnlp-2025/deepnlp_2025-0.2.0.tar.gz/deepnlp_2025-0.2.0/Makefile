# To do stuff with make, you type `make` in a directory that has a file called
# "Makefile".  You can also type `make -f <makefile>` to use a different filename.
#
# A Makefile is a collection of rules. Each rule is a recipe to do a specific
# thing, sort of like a grunt task or an npm package.json script.
#
# A rule looks like this:
#
# <target>: <prerequisites...>
# 	<commands>
#
# The "target" is required. The prerequisites are optional, and the commands
# are also optional, but you have to have one or the other.
#
# Type `make` to show the available targets and a description of each.
#
.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Clean-up

clean: ## run all clean commands
	@poe clean

##@ Git Branches

show-branches: ## show all branches
	@git show-branch --list

dev-checkout: ## checkout the dev branch
	@branch=$(shell echo $${branch:-"dev"}) && \
	    git show-branch --list | grep -q $${branch} && \
		git checkout $${branch}

dev-checkout-upstream: ## create and checkout the dev branch, and set the upstream
	@branch=$(shell echo $${branch:-"dev"}) && \
		git checkout -B $${branch} && \
		git push --set-upstream origin $${branch} || true

main-checkout: ## checkout the main branch
	@git checkout main

##@ Utilities

large-files: ## show the 20 largest files in the repo
	@find . -printf '%s %p\n'| sort -nr | head -20

disk-usage: ## show the disk usage of the repo
	@du -h -d 2 .

git-sizer: ## run git-sizer
	@git-sizer --verbose

gc-prune: ## garbage collect and prune
	@git gc --prune=now

##@ Setup

install-node: ## install node
	@export NVM_DIR="$${HOME}/.nvm"; \
	[ -s "$${NVM_DIR}/nvm.sh" ] && . "$${NVM_DIR}/nvm.sh"; \
	nvm install --lts

nvm-ls: ## list node versions
	@export NVM_DIR="$${HOME}/.nvm"; \
	[ -s "$${NVM_DIR}/nvm.sh" ] && . "$${NVM_DIR}/nvm.sh"; \
	nvm ls

set-default-node: ## set default node
	@export NVM_DIR="$${HOME}/.nvm"; \
	[ -s "$${NVM_DIR}/nvm.sh" ] && . "$${NVM_DIR}/nvm.sh"; \
	nvm alias default node

install-pipx: ## install pipx (pre-requisite for external tools)
	@command -v pipx &> /dev/null || pip install --user pipx || true

install-copier: install-pipx ## install copier (pre-requisite for init-project)
	@command -v copier &> /dev/null || pipx install copier || true

install-uv: ## install uv (pre-requisite for install)
	@command -v uv &> /dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh || true

install-poe: install-pipx ## install poetry (pre-requisite for install)
	@command -v poe &> /dev/null || pipx install poethepoet || true

install-commitzen: install-pipx ## install commitzen (pre-requisite for commit)
	@command -v cz &> /dev/null || pipx install commitizen || true

install-precommit: install-pipx ## install pre-commit
	@command -v pre-commit &> /dev/null || pipx install pre-commit || true

install-precommit-hooks: install-precommit ## install pre-commit hooks
	@pre-commit install

install: install-uv ## install virtual environment with uv and pre-commit hooks
	@uv sync --all-extras
	@uv run pre-commit install

initialize: install-pipx ## initialize the project environment
	@pipx install copier
	@pipx install poethepoet
	@pipx install commitizen
	@pipx install pre-commit
	@pre-commit install

init-project: initialize remove-template ## initialize the project (Warning: do this only once!)
	@copier copy --trust --answers-file .copier-config.yaml gh:entelecheia/hyperfast-course-template .

reinit-project: install-copier ## reinitialize the project (Warning: this may overwrite existing files!)
	@bash -c 'args=(); while IFS= read -r file; do args+=("--skip" "$$file"); done < .copierignore; copier copy --trust "$${args[@]}" --answers-file .copier-config.yaml gh:entelecheia/hyperfast-course-template .'
##@ Development

sync: ## sync dependencies using uv
	@uv sync

sync-all: ## sync dependencies with all extras using uv
	@uv sync --all-extras

lock: ## lock dependencies using uv
	@uv lock

lock-upgrade: ## upgrade and lock dependencies using uv
	@uv lock --upgrade

check: ## run all code quality checks (lint, type check, dependency check)
	@uv run ruff check src/
	@uv run mypy --config-file pyproject.toml src/
	@uv run deptry .

lint: ## run ruff linter
	@uv run ruff check src/

format: ## format code using ruff
	@uv run ruff format src/
	@uv run ruff check --fix src/

type-check: ## run mypy type checker
	@uv run mypy --config-file pyproject.toml src/

dep-check: ## check for obsolete dependencies
	@uv run deptry .

test: ## run tests with coverage
	@uv run pytest --cov=src --cov-report=xml --cov-report=html

test-cov-fail:
	@uv run pytest --cov=src --cov-report=xml --cov-fail-under=50 --junitxml=tests/pytest.xml | tee tests/pytest-coverage.txt

test-quick: ## run tests without coverage
	@uv run pytest

build: ## build wheel file using hatchling
	@uv build

publish: ## publish to PyPI (requires credentials)
	@uv build
	@uvx twine upload dist/*

test-publish: ## publish to test PyPI
	@uv build
	@uvx twine upload --repository testpypi dist/*

docs: ## Build and serve the documentation
	@bash book/_scripts/build.sh && echo "📚 Documentation built successfully"
