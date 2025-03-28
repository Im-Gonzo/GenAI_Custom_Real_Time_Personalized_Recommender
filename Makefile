#############################
#	MAKEFILE CONFIGURATION	#
#############################
BLUE := \033[1;34m
GREEN := \033[1;32m
RED := \033[1;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

#############################
#	TOOLS CONFIGURATION		#
#############################

# Configuration
PYTHON := python3
TERRAFORM := terraform
GCLOUD := gcloud

#############################
#	INFRA CONFIGURATION		#
#############################

PROJECT_ID ?= recsys-dev-gonzo-1
REGION ?= us-central1
ZONE ?= us-central1-a

VERTEX_FEATURE_STORE_ID ?= recsys_dev_feature_store
VERTEX_FEATURE_STORE_INSTANCE_ID ?= recsys-dev-instance-store
BIGQUERY_DATASET_ID ?= recsys_dev_retail_dataset

GCP_ARTIFACT_REGISTRY ?= recsys-dev-artifact-registry

GCS_DATA_BUCKET ?= recsys-dev-data

GEMINI_AGENT_ID ?= recsys-dev-recommender-agent

.PHONY: help setup install-tools verify-tools setup-gcp setup-local tf-init tf-plan tf-apply tf-destroy format lint test

help: ## Show this help message
	@echo '${BLUE}Usage:${NC}'
	@echo '  make ${GREEN}<target>${NC}'
	@echo ''
	@echo '${BLUE}Targets:${NC}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: setup-gcp setup-local setup-tf## Complete setup process

setup-gcp: ## Set up GCP project and enable APIs
	@echo "${BLUE}Setting up GCP project...${NC}"
	@gcloud projects create $(PROJECT_ID) --name="Recommender System" || true
	@gcloud config set project $(PROJECT_ID)
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
	@sed -i '' 's/GCP_PROJECT=.*/GCP_PROJECT=$(PROJECT_ID)/g' .env
	@sed -i '' 's/GCP_LOCATION=.*/GCP_LOCATION=$(REGION)/g' .env
	@sed -i '' 's|GCP_CREDENTIALS=.*|GCP_CREDENTIALS=$(PWD)/terraform-sa-key.json|g' .env
	@sed -i '' 's/PROJECT_ID=.*/PROJECT_ID=$(PROJECT_ID)/g' .env
	@sed -i '' 's/REGION=.*/REGION=$(REGION)/g' .env
	@sed -i '' 's/ZONE=.*/ZONE=$(ZONE)/g' .env
	@sed -i '' 's/VERTEX_FEATURE_STORE_ID=.*/VERTEX_FEATURE_STORE_ID=$(VERTEX_FEATURE_STORE_ID)/g' .env
	@sed -i '' 's/VERTEX_FEATURE_STORE_INSTANCE_ID=.*/VERTEX_FEATURE_STORE_INSTANCE_ID=$(VERTEX_FEATURE_STORE_INSTANCE_ID)/g' .env
	@sed -i '' 's/BIGQUERY_DATASET_ID=.*/BIGQUERY_DATASET_ID=$(BIGQUERY_DATASET_ID)/g' .env
	@sed -i '' 's/GCP_ARTIFACT_REGISTRY=.*/GCP_ARTIFACT_REGISTRY=$(GCP_ARTIFACT_REGISTRY)/g' .env
	@sed -i '' 's/GCP_MODEL_REGISTRY=.*/GCP_MODEL_REGISTRY=$(GCP_MODEL_REGISTRY)/g' .env
	@sed -i '' 's/GCS_DATA_BUCKET=.*/GCS_DATA_BUCKET=$(GCS_DATA_BUCKET)/g' .env
	@sed -i '' 's/GEMINI_AGENT_ID=.*/GEMINI_AGENT_ID=$(GEMINI_AGENT_ID)/g' .env
	@echo "${GREEN}.env updated successfully${NC}"

setup-tf: ## Set up variables.tf
	@echo "${BLUE} Setting up terraform variables file ${BLUE}"
	@sed -i '' 's|default[ ]*=[ ]*".*" # PROJECT_ID|default     = "$(PROJECT_ID)" # PROJECT_ID|g' terraform/variables.tf
	@sed -i '' 's|default[ ]*=[ ]*".*" # REGION|default     = "$(REGION)" # REGION|g' terraform/variables.tf
	@sed -i '' 's|default[ ]*=[ ]*".*" # VERTEX_FEATURE_STORE_ID|default     = "$(VERTEX_FEATURE_STORE_ID)" # VERTEX_FEATURE_STORE_ID|g' terraform/variables.tf
	@sed -i '' 's|default[ ]*=[ ]*".*" # BIGQUERY_DATASET_ID|default     = "$(BIGQUERY_DATASET_ID)" # BIGQUERY_DATASET_ID|g' terraform/variables.tf
	@sed -i '' 's|default[ ]*=[ ]*".*" # GCP_ARTIFACT_REGISTRY|default     = "$(GCP_ARTIFACT_REGISTRY)" # GCP_ARTIFACT_REGISTRY|g' terraform/variables.tf
	@sed -i '' 's|name[ ]*=[ ]*".*" # GCS_DATA_BUCKET|name          = "$(GCS_DATA_BUCKET)" # GCS_DATA_BUCKET|g' terraform/variables.tf
	@echo "${GREEN}terraform/variables.tf updated successfully${NC}"

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