resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-lambda-role-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.project_name}-lambda-policy-${var.environment}"
  description = "Policy for Operations Agent Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Effect = "Allow"
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ]
          Resource = "arn:aws:logs:${var.region}:${var.account_id}:*"
        },
        {
          Effect = "Allow"
          Action = [
            "dynamodb:GetItem",
            "dynamodb:PutItem",
            "dynamodb:Query",
            "dynamodb:UpdateItem"
          ]
          Resource = [
            var.conversations_table_arn,
            "${var.conversations_table_arn}/*",
            var.pipelines_table_arn,
            "${var.pipelines_table_arn}/*"
          ]
        },
        {
          Effect = "Allow"
          Action = [
            "logs:FilterLogEvents",
            "logs:DescribeLogStreams",
            "logs:GetLogEvents"
          ]
          Resource = "arn:aws:logs:${var.region}:${var.account_id}:log-group:*"
        },
        {
          Effect = "Allow"
          Action = [
            "states:ListExecutions",
            "states:DescribeExecution",
            "states:DescribeStateMachine"
          ]
          Resource = "arn:aws:states:${var.region}:${var.account_id}:*"
        }
      ],
      var.bedrock_model_id != "" ? [
        {
          Effect = "Allow"
          Action = [
            "bedrock:InvokeModel"
          ]
          Resource = "arn:aws:bedrock:${var.region}::foundation-model/*"
        }
      ] : []
    )
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
