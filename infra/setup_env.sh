#!/bin/bash
# Setup script for Terraform environment variables
# This ensures sensitive data is not stored in files

set -e

echo "🔐 Terraform Environment Setup"
echo "================================"
echo ""

# Check if OpenAI API key is already set
if [ -z "$TF_VAR_openai_api_key" ]; then
    echo "⚠️  TF_VAR_openai_api_key is not set"
    echo ""
    echo "To set it, run:"
    echo "  export TF_VAR_openai_api_key=\"your-key-here\""
    echo ""
    echo "Or create a .env file in the infra/ directory with:"
    echo "  TF_VAR_openai_api_key=\"your-key-here\""
    echo ""
    echo "Then source it:"
    echo "  source .env"
    echo ""
    read -p "Do you want to set it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -sp "Enter your OpenAI API key: " api_key
        echo ""
        export TF_VAR_openai_api_key="$api_key"
        echo "✓ API key set for this session"
        echo ""
        echo "To make it persistent, add to your ~/.zshrc or ~/.bashrc:"
        echo "  export TF_VAR_openai_api_key=\"$api_key\""
    fi
else
    echo "✓ TF_VAR_openai_api_key is set"
fi

echo ""
echo "Current Terraform variables:"
echo "  AWS Region: ${TF_VAR_aws_region:-us-east-1 (default)}"
echo "  Project Name: ${TF_VAR_project_name:-ops-agent (default)}"
echo "  Environment: ${TF_VAR_environment:-prod (default)}"
echo "  OpenAI API Key: ${TF_VAR_openai_api_key:+***SET***}${TF_VAR_openai_api_key:-NOT SET}"

echo ""
echo "To apply Terraform:"
echo "  cd infra"
echo "  terraform init"
echo "  terraform plan"
echo "  terraform apply"
