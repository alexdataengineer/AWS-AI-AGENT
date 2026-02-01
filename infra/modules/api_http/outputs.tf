output "api_id" {
  description = "API Gateway HTTP API ID"
  value       = aws_apigatewayv2_api.http_api.id
}

output "api_invoke_url" {
  description = "API Gateway HTTP API invoke URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "api_execution_arn" {
  description = "API Gateway HTTP API execution ARN"
  value       = aws_apigatewayv2_api.http_api.execution_arn
}
