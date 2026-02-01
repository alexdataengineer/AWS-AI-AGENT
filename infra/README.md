# Terraform Infrastructure

This directory contains the Terraform configuration for the Operations Agent.

## Structure

```
infra/
├── main.tf                 # Main configuration
├── variables.tf            # Variable definitions
├── outputs.tf             # Output values
├── versions.tf            # Terraform and provider versions
├── terraform.tfvars       # Variable values (create from example)
└── modules/
    ├── dynamodb/          # DynamoDB tables module
    ├── iam/               # IAM roles and policies module
    ├── lambda_agent/      # Lambda function module
    └── api_http/          # API Gateway HTTP API module
```

## Quick Start

1. Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values

3. Initialize Terraform:
```bash
terraform init
```

4. Review the plan:
```bash
terraform plan
```

5. Apply the configuration:
```bash
terraform apply
```

6. Get the API endpoint:
```bash
terraform output api_invoke_url
```

## Variables

See `variables.tf` for all available variables. Key variables:

- `aws_region`: AWS region for resources
- `project_name`: Project name for resource naming
- `environment`: Environment name (dev, staging, prod)
- `bedrock_model_id`: Optional Bedrock model ID
- `log_retention_days`: CloudWatch Logs retention
- `lambda_timeout`: Lambda function timeout
- `lambda_memory_size`: Lambda function memory

## Outputs

- `api_invoke_url`: API Gateway HTTP API invoke URL
- `lambda_function_name`: Lambda function name
- `lambda_function_arn`: Lambda function ARN
- `conversations_table_name`: DynamoDB conversations table name
- `pipelines_table_name`: DynamoDB pipelines catalog table name
- `api_gateway_id`: API Gateway HTTP API ID

## Module Details

### DynamoDB Module
Creates two tables:
- Conversations table with TTL
- Pipelines catalog table

### IAM Module
Creates Lambda execution role with minimal required permissions:
- DynamoDB access
- CloudWatch Logs access
- Step Functions access
- Bedrock access (if model ID provided)

### Lambda Module
Creates:
- Lambda function with Python 3.11
- CloudWatch Log Group
- Packages code from `../lambda` directory

### API Gateway Module
Creates:
- HTTP API
- POST /chat route
- Lambda integration
- CORS configuration
- Access logging

## Destroying Resources

To remove all resources:
```bash
terraform destroy
```

## Notes

- The Lambda function code is packaged from the `../lambda` directory
- Ensure you have appropriate AWS credentials configured
- Review IAM policies before applying in production
- Consider adding API keys or authentication for production use
