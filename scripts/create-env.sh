#!/bin/bash

# Script to create Azure OpenAI deployment and generate .env file automatically
# No user input required - runs with predefined defaults
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Predefined values - no user input needed
UNIQUE_ID=$(openssl rand -hex 2 | tr '[:lower:]' '[:upper:]')
RESOURCE_GROUP="rg-adr-agent-${UNIQUE_ID}"
LOCATION="swedencentral"
OPENAI_ACCOUNT_NAME="oai-adr-agent-${UNIQUE_ID}"
DEPLOYMENT_NAME="gpt-4.1"
MODEL_NAME="gpt-4.1"
MODEL_VERSION="2025-04-14"
SKU_NAME="GlobalStandard"
SKU_CAPACITY=20
API_VERSION="2024-12-01-preview"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================"
echo "Azure OpenAI Deployment Automation"
echo "========================================"

print_status "Using predefined configuration:"
print_status "  Resource Group: $RESOURCE_GROUP"
print_status "  Location: $LOCATION"
print_status "  OpenAI Account: $OPENAI_ACCOUNT_NAME"
print_status "  Deployment: $DEPLOYMENT_NAME ($MODEL_NAME $MODEL_VERSION)"

# Check if Azure CLI is installed and user is logged in
print_status "Checking Azure CLI installation and login status..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_success "Azure CLI is available and you are logged in"

# Check if resource group exists, create if it doesn't
print_status "Checking if resource group '$RESOURCE_GROUP' exists..."
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    print_status "Resource group '$RESOURCE_GROUP' doesn't exist. Creating it..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    print_success "Resource group '$RESOURCE_GROUP' created successfully"
else
    print_success "Resource group '$RESOURCE_GROUP' already exists"
fi

# Check if OpenAI account exists, create if it doesn't
print_status "Checking if OpenAI account '$OPENAI_ACCOUNT_NAME' exists..."
if ! az cognitiveservices account show --name "$OPENAI_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_status "OpenAI account '$OPENAI_ACCOUNT_NAME' doesn't exist. Creating it..."
    az cognitiveservices account create \
        --name "$OPENAI_ACCOUNT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --kind OpenAI \
        --sku S0 \
        --yes
    print_success "OpenAI account '$OPENAI_ACCOUNT_NAME' created successfully"
else
    print_success "OpenAI account '$OPENAI_ACCOUNT_NAME' already exists"
fi

# Create deployment
print_status "Creating deployment '$DEPLOYMENT_NAME'..."
az cognitiveservices account deployment create \
    --name "$OPENAI_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --deployment-name "$DEPLOYMENT_NAME" \
    --model-name "$MODEL_NAME" \
    --model-version "$MODEL_VERSION" \
    --model-format OpenAI \
    --sku-capacity "$SKU_CAPACITY" \
    --sku-name "$SKU_NAME"

print_success "Deployment '$DEPLOYMENT_NAME' created successfully"

# Get the endpoint and API key
print_status "Retrieving endpoint and API key..."
ENDPOINT=$(az cognitiveservices account show \
    --name "$OPENAI_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.endpoint" \
    --output tsv)

API_KEY=$(az cognitiveservices account keys list \
    --name "$OPENAI_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "key1" \
    --output tsv)

# Create .env file
ENV_FILE="/workspaces/adr-agent/.env"
print_status "Creating .env file at $ENV_FILE..."

cat > "$ENV_FILE" << EOF
AZURE_OPEN_AI_DEPLOYMENT_NAME=$DEPLOYMENT_NAME
AZURE_OPEN_AI_API_KEY=$API_KEY
AZURE_OPEN_AI_ENDPOINT=$ENDPOINT
AZURE_OPEN_AI_API_VERSION=$API_VERSION
EOF

print_success ".env file created successfully"

# Display summary
echo ""
echo "========================================="
echo "Azure OpenAI Deployment Summary"
echo "========================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "OpenAI Account: $OPENAI_ACCOUNT_NAME"
echo "Deployment Name: $DEPLOYMENT_NAME"
echo "Model: $MODEL_NAME ($MODEL_VERSION)"
echo "Endpoint: $ENDPOINT"
echo "API Version: $API_VERSION"
echo "========================================="
echo ""
print_success "Setup completed successfully! Your .env file has been created with the deployment details."
print_warning "Keep your API key secure and don't commit the .env file to version control."