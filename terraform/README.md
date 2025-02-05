# Infrastructure as Code for Recommender System

This directory contains the Terraform configurations for deploying the recommender system infrastructure on Google Cloud Platform (GCP).

## Prerequisites

- An active GCP project
- Service account with necessary permissions
- Service account key file

## Infrastructure Overview

```mermaid
graph TB
    subgraph GCP Project
        subgraph "Vertex AI"
            FS[Feature Store]
            subgraph "Models"
                TT[Two-Tower Model]
                RM[Ranking Model]
            end
            subgraph "Endpoints"
                TTE[Two-Tower Endpoint]
                RME[Ranking Endpoint]
            end
            subgraph "Agent"
                GA[Gemini Agent]
                GP[Gemini Pro]
            end
            MON[Model Monitoring]
        end

        subgraph "Storage"
            GCS1[Data Bucket]
            GCS2[Model Bucket]
            GCS3[Artifact Bucket]
            AR[Artifact Registry]
        end

        subgraph "IAM"
            SA[Service Account]
            ROLES[IAM Roles]
        end

        TT --> TTE
        RM --> RME
        GP --> GA
        FS --> TTE
        FS --> RME
        FS --> GA
        SA --> FS
        SA --> TT
        SA --> RM
        SA --> GA
        SA --> GCS1
        SA --> GCS2
        SA --> GCS3
        SA --> AR
        ROLES --> SA
        MON --> TTE
        MON --> RME
    end

    style GA fill:#f9f,stroke:#333
    style GP fill:#f9f,stroke:#333
```

## Module Structure

```
terraform/
├── main.tf                 # Main configuration file
├── variables.tf            # Input variables
├── outputs.tf             # Output definitions
├── terraform.tfvars.example # Example variable values
└── modules/
    ├── feature-store/     # Vertex AI Feature Store
    ├── vertex-ai/         # Models, Endpoints, and Gemini Agent
    ├── storage/           # GCS and Artifact Registry
    └── iam/               # IAM and Service Accounts
```

[Rest of the README content remains the same...]