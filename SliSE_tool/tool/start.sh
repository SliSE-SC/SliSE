#!/bin/bash

# Check if a .sol file path is provided
if [ -z "$1" ]; then
  echo "Error: Please provide the path to a .sol file as an argument."
  echo "Usage: $0 <sol_file_path>"
  exit 1
fi

# Get the .sol file path
SOL_FILE="$1"

# Debug info: Print the current working directory
echo "Current working directory: $(pwd)"

# Debug info: Check if the Docker image exists
echo "Checking if Docker image slise_image exists..."
docker images slise_image

if [ $? -ne 0 ]; then
  echo "Error: Docker image slise_image does not exist. Please build the image first."
  exit 1
fi

# Run the Docker container
docker run -it \
  -v $(pwd):/SliSE_dev/SliSE/SliSE \
  -v $(pwd)/detectiion_output:/SliSE_dev/SliSE/SliSE/detectiion_output \
  slise_image bash -c "source /SliSE_dev/py38/py38/bin/activate && python /SliSE_dev/SliSE/SliSE/SliSE.py -s /SliSE_dev/SliSE/SliSE/$SOL_FILE -vt reentrancy"

# Check if the Docker command executed successfully
if [ $? -eq 0 ]; then
  echo "Docker container ran successfully! Results are saved in $(pwd)/detectiion_output/"
else
  echo "Error: Docker container failed to run."
  exit 1
fi