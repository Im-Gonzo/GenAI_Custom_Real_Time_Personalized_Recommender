# GenAI Real-Time Personalized Recommender

A real-time recommender system using GCP Vertex AI, Feature Store, and Gemini for personalized recommendations.

## Project Structure 📁

```
.
├── recsys/               # Main recommender system code
├── terraform/            # Infrastructure as Code
├── notebooks/           # Jupyter notebooks for experiments
├── pyproject.toml      # Poetry dependencies
└── poetry.lock         # Poetry lock file
```

## Prerequisites 📋

- Python 3.11+
- Poetry
- Terraform 1.0+
- Google Cloud SDK
- Make

## Quick Start 🚀

```bash
# Install tools and set up environment
make setup

# Configure infrastructure
make deploy-all
```

## Development Setup 🛠️

1. **Install Dependencies**
   ```bash
   # Install Poetry if not installed
   curl -sSL https://install.python-poetry.org | python3 -

   # Set up development environment
   make dev-setup
   ```

2. **Configure GCP**
   ```bash
   # Set up GCP project and enable APIs
   make setup-gcp
   ```

3. **Set Up Local Environment**
   ```bash
   # Configure local environment
   make setup-local
   ```

## Infrastructure Management 🏗️

```bash
# Initialize Terraform
make tf-init

# Plan changes
make tf-plan

# Apply changes
make tf-apply

# Destroy infrastructure
make tf-destroy
```

## Code Quality 🧹

```bash
# Format code (Python & Terraform)
make format

# Run linting
make lint

# Run tests
make test
```

## Infrastructure Components 🌐

- **Vertex AI Feature Store**
  - Customer features
  - Article features
  - Interaction features

- **Models**
  - Two-Tower Model for retrieval
  - Ranking Model for scoring
  - Gemini Agent for LLM ranking

- **Storage**
  - Data buckets
  - Model artifacts
  - Feature data

## Available Make Commands 🛠️

Run `make help` to see all available commands. Key commands include:

```bash
make setup              # Complete setup process
make deploy-all         # Deploy full infrastructure
make status            # Check system status
make logs              # View component logs
make clean             # Clean up local files
```

## Development Workflow 👩‍💻

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   ```bash
   # Format code
   make format

   # Run tests
   make test
   ```

3. **Commit Changes**
   ```bash
   make commit
   ```

4. Open Pull Request

## Documentation 📚

- [Infrastructure Details](terraform/README.md)
- [Local Setup Guide](LOCAL_SETUP.md)
- [Feature Store Documentation](recsys/features/README.md)

## Troubleshooting 🔧

1. **Authentication Issues**
   ```bash
   make auth-fix
   ```

2. **Infrastructure State**
   ```bash
   make tf-refresh
   ```

3. **Environment Issues**
   ```bash
   make fix-env
   ```

## License 📄

MIT License. See [LICENSE](LICENSE) for details.