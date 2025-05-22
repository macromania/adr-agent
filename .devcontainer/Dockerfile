FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    curl \
    git \
    gnupg \
    jq \
    sudo \
    ca-certificates \
    unzip \
    wget \
    gnupg2 \
    pass \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Set up workspace directory
WORKDIR /workspaces/adr-agent

# Set environment variables
ENV PATH="/root/.local/bin/:$PATH"
ENV PYTHONPATH=/workspaces/fjords
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set up non-root user permissions
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode