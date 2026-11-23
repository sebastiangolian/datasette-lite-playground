# Datasette Lite playground - build, serve and test the GitHub Pages site.

SITE_DIR := site
PORT ?= 8009
LIVE_URL ?= https://sebastiangolian.github.io/datasette-lite-playground/
VENV := .venv
PYTHON := $(VENV)/bin/python
# Single source of truth for the pinned Datasette Lite commit: the deploy workflow.
DATASETTE_LITE_REF ?= $(shell sed -n 's/^ *DATASETTE_LITE_REF: *//p' .github/workflows/deploy-pages.yml)
LITE_FILES := index.html shell.js sw.js webworker.js

.DEFAULT_GOAL := help
.PHONY: help build serve venv test test-local test-live clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-11s\033[0m %s\n", $$1, $$2}'

# The self-hosted copy has Plausible analytics removed - it reports to lite.datasette.io.
build: ## Build the site into site/ (data, poland.db, self-hosted Datasette Lite)
	rm -rf $(SITE_DIR)
	mkdir -p $(SITE_DIR)/data $(SITE_DIR)/lite
	cp index.html $(SITE_DIR)/
	cp data/* $(SITE_DIR)/data/
	python3 scripts/build_db.py $(SITE_DIR)/data/poland.db
	curl -sSfL "https://github.com/simonw/datasette-lite/archive/$(DATASETTE_LITE_REF).tar.gz" \
		| tar -xz --strip-components=1 -C $(SITE_DIR)/lite \
			$(addprefix datasette-lite-$(DATASETTE_LITE_REF)/,$(LITE_FILES))
	sed -i.bak '/plausible/d' $(SITE_DIR)/lite/index.html && rm $(SITE_DIR)/lite/index.html.bak
	@echo "Built $(SITE_DIR)/ with datasette-lite@$(DATASETTE_LITE_REF)"

serve: build ## Build and serve the site on http://localhost:8009/ (override with PORT=)
	python3 -m http.server $(PORT) -d $(SITE_DIR)

$(PYTHON): requirements-dev.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -q -r requirements-dev.txt
	touch $(PYTHON)

venv: $(PYTHON) ## Create .venv with test dependencies (uses installed Google Chrome)

test: test-local ## Alias for test-local

test-local: build venv ## Serve site/ locally and check the self-hosted scenarios
	@python3 -m http.server $(PORT) -d $(SITE_DIR) >/dev/null 2>&1 & \
		pid=$$!; trap 'kill $$pid' EXIT; sleep 1; \
		$(PYTHON) tests/check_scenarios.py http://localhost:$(PORT)/ --host self

test-live: venv ## Check every scenario link (both hosts) on the deployed site
	$(PYTHON) tests/check_scenarios.py $(LIVE_URL)

clean: ## Remove build output and the virtualenv
	rm -rf $(SITE_DIR) $(VENV)
