# =============================================================================
# AutomationExercise API Test Framework — Makefile
# Usage: make <target>
# =============================================================================

.PHONY: install smoke regression products brands search auth user clean help

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------

install:
	pip install -r requirements.txt

# --------------------------------------------------------------------------
# Test runs
# --------------------------------------------------------------------------

smoke:
	pytest -m smoke -v

regression:
	pytest -v

products:
	pytest -m products -v

brands:
	pytest -m brands -v

search:
	pytest -m search -v

auth:
	pytest -m auth -v

user:
	pytest -m user -v

positive:
	pytest -m positive -v

negative:
	pytest -m negative -v

# Run with parallel workers (requires pytest-xdist)
parallel:
	pytest -n auto -v

# Dry-run: collect tests without executing
collect:
	pytest --collect-only -q

# --------------------------------------------------------------------------
# Cleanup
# --------------------------------------------------------------------------

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf reports/report.html allure-results/ allure-report/
	@echo "Cleaned up."

# --------------------------------------------------------------------------
# Help
# --------------------------------------------------------------------------

help:
	@echo ""
	@echo "  make install     Install all dependencies"
	@echo "  make smoke       Run smoke tests only"
	@echo "  make regression  Run full regression suite"
	@echo "  make products    Run products API tests (API 1-2)"
	@echo "  make brands      Run brands API tests (API 3-4)"
	@echo "  make search      Run search API tests (API 5-6)"
	@echo "  make auth        Run auth API tests (API 7-10)"
	@echo "  make user        Run user account API tests (API 11-14)"
	@echo "  make positive    Run all positive tests"
	@echo "  make negative    Run all negative tests"
	@echo "  make parallel    Run full suite in parallel"
	@echo "  make collect     Dry-run: list all collected tests"
	@echo "  make clean       Remove cache and report artifacts"
	@echo ""
