.PHONY: build up down clean

# Dockerfile building using our Python script
BUILD_COMMAND := python3 build_dockerfile.py

# Path to the JupyterLab Dockerfile template
JUPYTERLAB_DOCKERFILE_TEMPLATE := jupyterlab/Dockerfile.template
JUPYTERLAB_DOCKERFILE := jupyterlab/Dockerfile
JUPYTERLAB_VALUES := jupyterlab/values.yaml
JUPYTERLAB_BASE := jupyterlab/base.yaml

build:
	@echo "Generating JupyterLab Dockerfile..."
	@$(BUILD_COMMAND) --values $(JUPYTERLAB_VALUES) --base $(JUPYTERLAB_BASE) --output $(JUPYTERLAB_DOCKERFILE)
	@echo "Building Docker images..."
	@docker compose build
	@echo "Cleaning up temporary files..."
	@rm -f jupyterlab/temp_*

up: build
	@echo "Starting Docker containers..."
	@docker compose up -d

down:
	@echo "Stopping Docker containers..."
	@docker compose down

clean:
	@echo "Cleaning up generated files and containers..."
	@docker compose down -v --remove-orphans
	@if [ -f $(JUPYTERLAB_DOCKERFILE) ]; then rm $(JUPYTERLAB_DOCKERFILE); fi
	@rm -f jupyterlab/temp_* 