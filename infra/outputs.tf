output "api_invoke_url" {
  description = "API Gateway HTTP API invoke URL"
  value       = module.api_gateway.api_invoke_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = module.lambda.lambda_function_arn
}

output "conversations_table_name" {
  description = "DynamoDB conversations table name"
  value       = module.dynamodb.conversations_table_name
}

output "pipelines_table_name" {
  description = "DynamoDB pipelines catalog table name"
  value       = module.dynamodb.pipelines_table_name
}

output "api_gateway_id" {
  description = "API Gateway HTTP API ID"
  value       = module.api_gateway.api_id
}
