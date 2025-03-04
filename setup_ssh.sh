#!/bin/bash

set -e  # Exit immediately if a command fails
set -o pipefail  # Prevents errors in pipelines from being masked

# Function to securely export environment variables
export_env_vars_from_file() {
    local env_file=$1
    if [ ! -f "$env_file" ]; then
        echo "Environment variables file not found: $env_file"
        return 1
    fi

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Allow only safe environment variable patterns (A-Z, 0-9, _)
        if [[ "$line" =~ ^[A-Z0-9_]+=.*$ ]]; then
            export "$line"
        else
            echo "Skipping unsafe environment variable: $line"
        fi
    done < "$env_file"
}

# Path to the captured environment variables file
ENV_VARS_FILE=/kaggle/working/kaggle_env_vars.txt

if [ -f "$ENV_VARS_FILE" ]; then
    echo "Exporting environment variables from $ENV_VARS_FILE"
    export_env_vars_from_file "$ENV_VARS_FILE"
else
    echo "Environment variables file not found. Skipping export."
fi

if [ "$#" -ne 1 ]; then
    echo "Usage: ./setup_ssh.sh <authorized_keys_url>"
    exit 1
fi

AUTH_KEYS_URL=$1

setup_ssh_directory() {
    SSH_DIR="/kaggle/working/.ssh"
    AUTH_KEYS_FILE="$SSH_DIR/authorized_keys"

    # Ensure parent directory is writable
    if [ ! -w "/kaggle/working" ]; then
        echo "The parent directory /kaggle/working is not writable."
        exit 1
    fi

    # Create SSH directory and set correct permissions
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    echo "Created SSH directory at $SSH_DIR"
    ls -ld "$SSH_DIR"  # Debugging: Check if the directory is created and its permissions

    echo "Downloading SSH authorized keys..."
    if wget -qO "$AUTH_KEYS_FILE" "$AUTH_KEYS_URL"; then
        # Validate that the file contains valid SSH keys before applying
        if grep -qE '^ssh-(rsa|ed25519|ecdsa)' "$AUTH_KEYS_FILE"; then
            chmod 600 "$AUTH_KEYS_FILE"
            echo "SSH keys downloaded and verified."
        else
            echo "Downloaded file does not contain valid SSH keys. Exiting."
            rm -f "$AUTH_KEYS_FILE"
            exit 1
        fi
    else
        echo "Failed to download authorized keys. Check the URL."
        exit 1
    fi
}

configure_sshd() {
    echo "Configuring SSH daemon..."

    mkdir -p /var/run/sshd

    cat <<EOF > /etc/ssh/sshd_config
Port 22
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile /kaggle/working/.ssh/authorized_keys
TCPKeepAlive yes
X11Forwarding no
IgnoreRhosts yes
HostbasedAuthentication no
PrintLastLog yes
ChallengeResponseAuthentication no
UsePAM yes
AcceptEnv LANG LC_*
AllowTcpForwarding no
GatewayPorts no
PermitTunnel no
ClientAliveInterval 60
ClientAliveCountMax 2
EOF

    echo "SSH configuration updated securely."
}

install_packages() {
    echo "Installing required packages..."
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends openssh-server
}

start_ssh_service() {
    echo "Starting SSH service..."
    service ssh restart
}

cleanup() {
    echo "Cleaning up temporary files..."
    rm -f /kaggle/working/kaggle_env_vars.txt
}

# Execute functions in a controlled manner
install_packages
setup_ssh_directory
configure_sshd
start_ssh_service
cleanup

echo "Setup script completed securely."
