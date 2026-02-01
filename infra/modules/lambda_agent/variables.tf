variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "lambda_role_arn" {
  description = "IAM role ARN for Lambda function"
  type        = string
}

variable "conversations_table" {
  description = "DynamoDB conversations table name"
  type        = string
}

variable "pipelines_table" {
  description = "DynamoDB pipelines catalog table name"
  type        = string
}

variable "default_region" {
  description = "Default AWS region"
  type        = string
}

variable "bedrock_model_id" {
  description = "Bedrock model ID (optional)"
  type        = string
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days"
  type        = number
  default     = 14
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}
