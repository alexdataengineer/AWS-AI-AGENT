provider "aws" {
  region = var.aws_region
}

provider "archive" {}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for current region
data "aws_region" "current" {}

# DynamoDB Tables
module "dynamodb" {
  source = "./modules/dynamodb"

  project_name = var.project_name
  environment  = var.environment
}

# IAM Role for Lambda
module "iam" {
  source = "./modules/iam"

  project_name            = var.project_name
  environment             = var.environment
  conversations_table_arn = module.dynamodb.conversations_table_arn
  pipelines_table_arn     = module.dynamodb.pipelines_table_arn
  account_id              = data.aws_caller_identity.current.account_id
  region                  = data.aws_region.current.name
  bedrock_model_id        = var.bedrock_model_id
}

# Lambda Function
module "lambda" {
  source = "./modules/lambda_agent"

  project_name            = var.project_name
  environment             = var.environment
  lambda_role_arn        = module.iam.lambda_role_arn
  conversations_table     = module.dynamodb.conversations_table_name
  pipelines_table         = module.dynamodb.pipelines_table_name
  default_region          = var.aws_region
  bedrock_model_id        = var.bedrock_model_id
  openai_api_key          = var.openai_api_key
  log_retention_days      = var.log_retention_days
  timeout                 = var.lambda_timeout
  memory_size             = var.lambda_memory_size
}

# API Gateway HTTP API
module "api_gateway" {
  source = "./modules/api_http"

  project_name    = var.project_name
  environment     = var.environment
  lambda_arn      = module.lambda.lambda_invoke_arn
  lambda_name     = module.lambda.lambda_function_name
  allowed_origins = var.allowed_origins
}
