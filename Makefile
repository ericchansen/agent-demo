# Fabric Sales Agent Accelerator — Makefile
# Usage: make <target>

RG ?= fsa-demo-rg
CAPACITY_NAME ?= fsa-demo-capacity

.PHONY: lint format format-check typecheck test test-eval \
        infra-validate infra-deploy infra-teardown load-data \
        demo diagrams clean

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

format-check:
	ruff format --check src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/unit/ -v

test-eval:
	python tests/eval/run_eval.py

infra-validate:
	az bicep build --file infra/main.bicep

infra-deploy:
	az deployment group create \
		--resource-group $(RG) \
		--template-file infra/main.bicep \
		--parameters infra/parameters/dev.bicepparam

infra-teardown:
	@echo "To pause Fabric capacity (saves cost when not in use):"
	@echo "  az fabric capacity suspend --capacity-name $(CAPACITY_NAME) --resource-group $(RG)"

load-data:
	python demo/load-wwi-data.py

demo:
	@echo "=== Fabric Sales Agent Accelerator — Demo ==="
	@echo ""
	@echo "v1 (Copilot CLI):"
	@echo "  1. Deploy infra:           make infra-deploy"
	@echo "  2. Load sample data:       make load-data"
	@echo "  3. Add Fabric MCP URL to your Copilot CLI MCP config"
	@echo "  4. Ask: 'Prepare an account plan for Tailspin Toys'"
	@echo ""
	@echo "v2 (Copilot SDK):"
	@echo "  python -m src.sdk.cli 'Prepare an account plan for Tailspin Toys'"

diagrams:
	python docs/diagrams/generate.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache .coverage
