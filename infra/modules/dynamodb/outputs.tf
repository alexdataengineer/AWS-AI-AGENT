output "conversations_table_name" {
  description = "Conversations table name"
  value       = aws_dynamodb_table.conversations.name
}

output "conversations_table_arn" {
  description = "Conversations table ARN"
  value       = aws_dynamodb_table.conversations.arn
}

output "pipelines_table_name" {
  description = "Pipelines catalog table name"
  value       = aws_dynamodb_table.pipelines_catalog.name
}

output "pipelines_table_arn" {
  description = "Pipelines catalog table ARN"
  value       = aws_dynamodb_table.pipelines_catalog.arn
}
