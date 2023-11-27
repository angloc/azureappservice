#!/bin/bash

# Ensure the Docker daemon socket is available to the vscode user
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock
sudo usermod -aG docker vscode

# Avoid problems with ownership by container versus host user
git config --global --add safe.directory '*'

# Install gitleaks
wget https://github.com/zricethezav/gitleaks/releases/download/v8.16.1/gitleaks_8.16.1_linux_x64.tar.gz
sudo tar -C /usr/local/bin -xzf gitleaks_8.16.1_linux_x64.tar.gz
rm gitleaks_8.16.1_linux_x64.tar.gz

# Install Python modules (if any) required to start the application build.
# Modules required by the application itself are installed in the
# application container(s) Docker build

pip3 install --user -r .devcontainer/devRequirements.txt

# Configure pre-commit
pre-commit install

az config set extension.use_dynamic_install=yes_without_prompt

# Install invoke alias

. ./.devcontainer/invalias.sh