#!/bin/bash

# List of extensions to install
extensions=(
  "ms-python.python"
  "ms-toolsai.jupyter"
  "CS50.ddb50"
  # Add more extensions here
)

# Install each extension sequentially with error handling
for extension in "${extensions[@]}"; do
  echo "Installing extension: $extension..."
  if code --install-extension "$extension"; then
    echo "Successfully installed: $extension"
  else
    echo "Failed to install: $extension" >&2
  fi
done

echo "All extensions have been processed."
