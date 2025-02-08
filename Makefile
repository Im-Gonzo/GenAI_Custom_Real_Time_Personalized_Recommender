# Colors for better output
BLUE := \033[1;34m
GREEN := \033[1;32m
RED := \033[1;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Configuration
PYTHON := python3
TERRAFORM := terraform
GCLOUD := gcloud

# Project configuration
PROJECT_ID ?= recsys-dev-gonzo
REGION ?= us-central1
ZONE ?= us-central1-a

.PHONY: help setup install-tools verify-tools setup-gcp setup-local tf-init tf-plan tf-apply tf-destroy format lint test

help: ## Show this help message
	@echo '${BLUE}Usage:${NC}'
	@echo '  make ${GREEN}<target>${NC}'
	@echo ''
	@echo '${BLUE}Targets:${NC}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: install-tools verify-tools setup-gcp setup-local ## Complete setup process

install-tools: ## Install required tools
	@echo "${BLUE}Installing required tools...${NC}"
	@if ! command -v brew &> /dev/null; then \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
	fi
	@if ! command -v terraform &> /dev/null; then \
		brew tap hashicorp/tap && brew install hashicorp/tap/terraform; \
	fi
	@if ! command -v gcloud &> /dev/null; then \
		brew install --cask google-cloud-sdk; \
	fi
	@if ! command -v poetry &> /dev/null; then \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@poetry install

verify-tools: ## Verify tool installations
	@echo "${BLUE}Verifying installations...${NC}"
	@terraform version || (echo "${RED}Terraform not installed${NC}" && exit 1)
	@gcloud version || (echo "${RED}Google Cloud SDK not installed${NC}" && exit 1)
	@poetry --version || (echo "${RED}Poetry not installed${NC}" && exit 1)
	@python3 --version || (echo "${RED}Python not installed${NC}" && exit 1)

setup-gcp: ## Set up GCP project and enable APIs
	@echo "${BLUE}Setting up GCP project...${NC}"
	@gcloud projects create $(PROJECT_ID) --name="Recommender System" || true
	@gcloud config set project $(PROJECT_ID)
	@for api in cloudresourcemanager.googleapis.com aiplatform.googleapis.com \
               artifactregistry.googleapis.com gemini.googleapis.com \
               iam.googleapis.com compute.googleapis.com; do \
		echo "Enabling $$api..."; \
		gcloud services enable $$api; \
	done
	@echo "${GREEN}Creating service account...${NC}"
	@gcloud iam service-accounts create terraform-sa \
		--description="Service Account for Terraform" \
		--display-name="Terraform Service Account" || true
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:terraform-sa@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/owner"
	@gcloud iam service-accounts keys create terraform-sa-key.json \
		--iam-account=terraform-sa@$(PROJECT_ID).iam.gserviceaccount.com

setup-local: ## Set up local environment
	@echo "${BLUE}Setting up local environment...${NC}"
	@cp .env.example .env
	@echo "GOOGLE_APPLICATION_CREDENTIALS=$(PWD)/terraform-sa-key.json" >> .env
	@echo "PROJECT_ID=$(PROJECT_ID)" >> .env
	@echo "REGION=$(REGION)" >> .env
	@echo "ZONE=$(ZONE)" >> .env

tf-init: ## Initialize Terraform
	@echo "${BLUE}Initializing Terraform...${NC}"
	@cd terraform && terraform init

tf-plan: ## Plan Terraform changes
	@echo "${BLUE}Planning Terraform changes...${NC}"
	@cd terraform && terraform plan

tf-apply: ## Apply Terraform changes
	@echo "${BLUE}Applying Terraform changes...${NC}"
	@cd terraform && terraform apply -auto-approve

tf-destroy: ## Destroy Terraform resources
	@echo "${RED}Destroying Terraform resources...${NC}"
	@cd terraform && terraform destroy

format: ## Format code
	@echo "${BLUE}Formatting code...${NC}"
	@terraform fmt -recursive terraform/
	@poetry run ruff format .

lint: ## Run linting
	@echo "${BLUE}Running linters...${NC}"
	@poetry run ruff check .
	@cd terraform && terraform fmt -check -recursive

test: ## Run tests
	@echo "${BLUE}Running tests...${NC}"
	@poetry run pytest

deploy-all: tf-init tf-plan tf-apply ## Deploy all resources

clean: ## Clean up local files
	@echo "${BLUE}Cleaning up...${NC}"
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type d -name ".pytest_cache" -exec rm -r {} +

auth-fix: ## Fix authentication issues
	@echo "${BLUE}Fixing authentication...${NC}"
	@gcloud auth application-default login
	@gcloud auth configure-docker

tf-refresh: ## Refresh Terraform state
	@echo "${BLUE}Refreshing Terraform state...${NC}"
	@cd terraform && terraform refresh

tf-clean: clean tf-init ## Clean and reinitialize Terraform

fix-env: ## Fix environment issues
	@echo "${BLUE}Fixing environment...${NC}"
	@cp .env.example .env
	@echo "${GREEN}Please update .env with your values${NC}"

# Development shortcuts
dev-setup: setup ## Setup development environment
	@echo "${BLUE}Setting up development environment...${NC}"
	@poetry install --with dev
	@pre-commit install