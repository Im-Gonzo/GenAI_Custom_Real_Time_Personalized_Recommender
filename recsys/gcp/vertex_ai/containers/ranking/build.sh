#!/bin/bash

# Set environment variables
PROJECT_ID=${PROJECT_ID:-recsys-dev-gonzo-2}
REGION=${REGION:-us-central1}
REPOSITORY=${REPOSITORY:-recsys-artifact-registry} 
IMAGE_NAME=recsys-ranking-predictor      
IMAGE_TAG=${IMAGE_TAG:-latest}

# Full image path
IMAGE_PATH=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Building Docker image for ranking container..."
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Repository: ${REPOSITORY}"
echo "Image: ${IMAGE_PATH}"

# Build the Docker image
echo "Building image..."
docker build -t ${IMAGE_PATH} .

# Configure Docker for Google Artifact Registry authentication
echo "Authenticating with Google Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Push the image to Google Artifact Registry
echo "Pushing image to Artifact Registry..."
docker push ${IMAGE_PATH}

echo "Successfully built and pushed ${IMAGE_PATH}"
echo "To deploy this image, update your Vertex AI endpoint configuration with this container image path."
