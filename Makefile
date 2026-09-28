# Local development: install the plugin from this checkout and refresh it after edits.
#
#   make install    add this checkout as a marketplace and install the plugin
#   make refresh    pick up local edits (reinstalls, since the cache is keyed by version)
#   make uninstall  remove the plugin and the marketplace
#   make test       run the script tests (RUN_LATEX=1 also compiles a PDF)
#
# Override the scope with SCOPE=project or SCOPE=local.
# Run /reload-plugins (or restart) in open sessions afterwards.

CLAUDE      ?= claude
PYTHON      ?= python3
CACHE       ?= $(HOME)/.claude/plugins/cache
SCOPE       ?= user
MARKETPLACE := z4n4-automated-research-skills
PLUGIN      := z4n4-automated-research
ROOT        := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: help install refresh uninstall validate verify list marketplace test

help:
	@echo "make install    add the local marketplace and install $(PLUGIN)"
	@echo "make refresh    validate, update the marketplace, and reinstall $(PLUGIN)"
	@echo "make uninstall  uninstall the plugin and remove the marketplace"
	@echo "make validate   validate the marketplace and plugin manifests"
	@echo "make verify     check that Claude's plugin cache matches this checkout"
	@echo "make list       show the installed $(PLUGIN) plugin"
	@echo "make test       run the script tests (RUN_LATEX=1 also compiles a PDF)"
	@echo "SCOPE=$(SCOPE)  (user | project | local)"

validate:
	$(CLAUDE) plugin validate $(ROOT)
	$(CLAUDE) plugin validate $(ROOT)/plugins/$(PLUGIN)

marketplace:
	@if $(CLAUDE) plugin marketplace list | grep -q "^ *❯ $(MARKETPLACE)$$"; then \
		$(CLAUDE) plugin marketplace update $(MARKETPLACE); \
	else \
		$(CLAUDE) plugin marketplace add $(ROOT) --scope $(SCOPE); \
	fi

install: validate marketplace
	$(CLAUDE) plugin install $(PLUGIN)@$(MARKETPLACE) --scope $(SCOPE)

refresh: validate marketplace
	@$(CLAUDE) plugin uninstall $(PLUGIN)@$(MARKETPLACE) --scope $(SCOPE) --keep-data >/dev/null 2>&1; \
		$(CLAUDE) plugin install $(PLUGIN)@$(MARKETPLACE) --scope $(SCOPE)
	@$(MAKE) --no-print-directory verify
	@echo "Refreshed. Run /reload-plugins in open Claude Code sessions."

# The cache lives at $(CACHE)/<marketplace>/<plugin>/<version>, the version read from plugin.json.
verify:
	@v=$$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' $(ROOT)/plugins/$(PLUGIN)/.claude-plugin/plugin.json | head -1); \
	dir=$(CACHE)/$(MARKETPLACE)/$(PLUGIN)/$$v; \
	if [ ! -d "$$dir" ]; then echo "✘ $(PLUGIN) $$v: not in cache ($$dir)"; exit 1; \
	elif diff -rq -x .DS_Store -x __pycache__ $(ROOT)/plugins/$(PLUGIN) "$$dir"; then echo "✔ $(PLUGIN) $$v: cache matches local"; \
	else echo "✘ $(PLUGIN) $$v: cache differs from local"; exit 1; fi

uninstall:
	-$(CLAUDE) plugin uninstall $(PLUGIN)@$(MARKETPLACE) --scope $(SCOPE)
	-$(CLAUDE) plugin marketplace remove $(MARKETPLACE)

list:
	@$(CLAUDE) plugin list | grep -A3 "@$(MARKETPLACE)" || echo "No $(MARKETPLACE) plugins installed."

test:
	$(PYTHON) -m unittest discover -s $(ROOT)/tests
