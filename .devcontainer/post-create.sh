echo "Scripts are being made executable..."
chmod +x /workspaces/adr-agent/scripts/*.sh || { echo "Failed to make scripts executable"; exit 1; }

echo "Setting up Python environment..."
/workspaces/adr-agent/scripts/restore.sh || { echo "Python environment setup failed"; exit 1; }