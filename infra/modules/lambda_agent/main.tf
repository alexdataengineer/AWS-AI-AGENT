data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/../lambda"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-handler-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-lambda-logs-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lambda_function" "ops_agent" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-handler-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = var.timeout
  memory_size      = var.memory_size
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DDB_CONVERSATIONS_TABLE = var.conversations_table
      DDB_PIPELINES_TABLE     = var.pipelines_table
      DEFAULT_REGION          = var.default_region
      BEDROCK_MODEL_ID        = var.bedrock_model_id
      OPENAI_API_KEY          = var.openai_api_key
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = {
    Name        = "${var.project_name}-handler-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

