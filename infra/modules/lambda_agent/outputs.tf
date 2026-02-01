output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.ops_agent.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.ops_agent.arn
}

output "lambda_invoke_arn" {
  description = "Lambda function invoke ARN"
  value       = aws_lambda_function.ops_agent.invoke_arn
}
