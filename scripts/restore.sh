# Install poetry if not installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 - || { echo "Failed to install Poetry"; exit 1; }
else
    echo "Poetry is already installed."
fi

# Create virtual environment if it doesn't exist
rm -rf .venv
poetry config virtualenvs.in-project true || { echo "Failed to configure Poetry for in-project virtualenv"; exit 1; }

# Check for requirements files
echo "Installing dependencies from pyproject.toml using poetry sync..."
poetry install || { echo "Failed to install dependencies with Poetry"; exit 1; }