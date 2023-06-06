#!/usr/bin/env bash

source ../.env

# Default values
USERNAME=""
PASSWORD=""
SRC_DIR="../"
DOCKER_BUILD=true

# RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Function for colorized logging
log() {
  local color=$1
  shift
  # shellcheck disable=SC2145
  echo -e "${color}$@${NC}"
}

# Function to display usage instructions
show_help() {
  echo "Usage: ./script.sh [OPTIONS]"
  echo "Docker builds and pushes Docker images to Docker Hub for each folder in the source directory that contains a Dockerfile."
  echo
  echo "Options:"
  echo "  -u, --username   Docker Hub or PyPI username (required)"
  echo "  -p, --password   Docker Hub or PyPI password (required)"
  echo "  -d, --directory  Source directory path (default: ../src)"
  echo "  -h, --help       Show help information"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
  -u | --username)
    USERNAME="$2"
    shift # past argument
    shift # past value
    ;;
  -p | --password)
    PASSWORD="$2"
    shift # past argument
    shift # past value
    ;;
  -d | --directory)
    SRC_DIR="$2"
    shift # past argument
    shift # past value
    ;;
  -h | --help)
    show_help
    exit 0
    ;;
  *) # unknown option
    echo "ERROR: Unknown option: $key"
    show_help
    exit 1
    ;;
  esac
done

create_docker_images() {
  # Iterate through each folder in the source directory
  for folder in "$SRC_DIR"/*/; do
    # Check if the folder contains a Dockerfile
    if [[ -f "$folder/Dockerfile" && "$DOCKER_BUILD" == true ]]; then
      # Extract the folder name
      folder_name=$(basename "$folder")

      # Login to Docker Hub
      log "${GREEN}" "Logging in to Docker Hub...${NC}"
      echo "$PASSWORD" | docker login -u "$USERNAME" --password-stdin

      # Docker build the Docker image
      log "${GREEN}" "Docker building Docker image for $folder_name...${NC}"
      docker build -t "$folder_name" "$folder"

      # Increment the Docker tag version
      next_version=latest
      log "${YELLOW}next_version=$next_version${NC}"

      # Tag the Docker image with the Docker Hub repository and version
      tag="${USERNAME}/${folder_name}:${next_version}"
      docker tag "$folder_name" "$tag"

      # Push the Docker image to Docker Hub
      log "${GREEN}" "Pushing Docker image to Docker Hub...${NC}"
      docker push "$tag"

      # Logout from Docker Hub
      log "${GREEN}" "Logging out from Docker Hub...${NC}"
      docker logout
    fi
  done
}

if [ "$DOCKER_BUILD" == true ]; then
  USERNAME="${DOCKER_USER}"
  PASSWORD="${DOCKER_PASSWORD}"
  create_docker_images
else
  echo "ERROR: username and password are required."
  exit 1
fi
