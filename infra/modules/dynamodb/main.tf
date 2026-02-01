resource "aws_dynamodb_table" "conversations" {
  name           = "${var.project_name}-conversations-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "conversation_id"
  range_key      = "timestamp"

  attribute {
    name = "conversation_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-conversations-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_dynamodb_table" "pipelines_catalog" {
  name         = "${var.project_name}-pipelines-catalog-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pipeline_name"

  attribute {
    name = "pipeline_name"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-pipelines-catalog-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}
