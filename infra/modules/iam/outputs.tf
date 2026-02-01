output "lambda_role_arn" {
  description = "IAM role ARN for Lambda function"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_role_name" {
  description = "IAM role name for Lambda function"
  value       = aws_iam_role.lambda_role.name
}
