variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "conversations_table_arn" {
  description = "ARN of conversations DynamoDB table"
  type        = string
}

variable "pipelines_table_arn" {
  description = "ARN of pipelines catalog DynamoDB table"
  type        = string
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "bedrock_model_id" {
  description = "Bedrock model ID (optional)"
  type        = string
  default     = ""
}
