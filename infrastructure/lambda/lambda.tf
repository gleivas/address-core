locals {
  function_name = "${var.service}_${var.function_name}_${terraform.workspace}"
  zip_path      = "${path.cwd}/.deploy/lambdas"
  zip_file      = "${local.zip_path}/${local.function_name}.zip"
  s3_key        = "lambda-code/${terraform.workspace}/${var.service}/${local.function_name}.zip"
}

# Lambda role and policies
resource "aws_iam_role" "this_lambda_role" {
  name = "${local.function_name}-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "${local.function_name}-lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup  ",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.this_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

# Lambda logs
resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention
}

# Lambda source code
data "external" "this_lambda_package" {
  program = concat(["python", "infrastructure/${path.module}/lambda_packer.py",
    local.zip_file,
    "-r ${var.requirements}", ], var.source_files
  )
  working_dir = "../"
}

# Lambda bucket
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "${var.service}-${terraform.workspace}-lambda-bucket"
}

resource "aws_s3_bucket_object" "this_lambda_code" {
  depends_on = ["data.external.this_lambda_package"]
  bucket     = aws_s3_bucket.lambda_bucket.id
  key        = local.s3_key
  source     = local.zip_file
  etag       = data.external.this_lambda_package.result.md5sum
}

# Lambda function
resource "aws_lambda_function" "this" {
  depends_on = [
    "aws_iam_role_policy_attachment.lambda_logs",
    "aws_cloudwatch_log_group.this",
    "aws_s3_bucket_object.this_lambda_code"
  ]

  function_name    = local.function_name
  role             = aws_iam_role.this_lambda_role.arn
  handler          = var.lambda_handler
  runtime          = var.runtime
  s3_bucket        = aws_s3_bucket.lambda_bucket.id
  s3_key           = local.s3_key
  source_code_hash = data.external.this_lambda_package.result.md5sum
  memory_size      = var.memory_size
  timeout          = var.timeout

  environment {
    variables = merge(var.env_vars,
      {
        log_level = "INFO"
      }
    )
  }

  tags = {
    env     = terraform.workspace
    service = var.service
  }
}

resource "aws_iam_role_policy_attachment" "this_lambda_additional_policies" {
  count      = length(var.additional_policies)
  role       = aws_iam_role.this_lambda_role.name
  policy_arn = var.additional_policies[count.index]
}