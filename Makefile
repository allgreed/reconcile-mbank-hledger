SOURCES := main.py main_test.py core.py
INPUTS := ~/Downloads/bork.html /tmp/sep.csv
ENTRYPOINT_DEPS := $(SOURCES) $(INPUTS)

# Porcelain
# ###############
.PHONY: container run lint test watch

enter_command = ls $(ENTRYPOINT_DEPS) | entr -c make --no-print-directory $(1)

watch:
	$(call enter_command,run)

run: setup ## run the app
	python3 main.py

lint: setup ## run static analysis
	@echo "Not implemented"; false

test: setup ## run all tests
	python3 -m pytest

iterate: 
	$(call enter_command,test)

container: build ## create container
	#docker build -t lmap .
	@echo "Not implemented"; false

# Plumbing
# ###############
.PHONY: setup gitclean gitclean-with-libs

setup:
gitclean:
	@# will remove everything in .gitignore expect for blocks starting with dep* or lib* comment

	diff --new-line-format="" --unchanged-line-format="" <(grep -v '^#' .gitignore | grep '\S' | sort) <(awk '/^# *(dep|lib)/,/^$/' testowy | head -n -1 | tail -n +2 | sort) | xargs rm -rf

gitclean-with-libs:
	diff --new-line-format="" --unchanged-line-format="" <(grep -v '^#' .gitignore | grep '\S' | sort) | xargs rm -rf

# Utilities
# ###############
.PHONY: help todo clean really_clean init
init: ## one time setup
	direnv allow .

todo: ## list all TODOs in the project
	git grep -I --line-number TODO | grep -v 'list all TODOs in the project' | grep TODO

clean: gitclean ## remove artifacts

really_clean: gitclean-with-libs ## remove EVERYTHING

help: ## print this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help
