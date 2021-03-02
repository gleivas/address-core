variable "service" {
  description = "The name of the service"
  type        = string
}

variable "api_version" {
  description = "The API version (only alphanumeric characters are allowed)"
  type        = string
}

variable "lambda_arn" {
  description = "The ARN of the lambda function"
  type        = string
}

variable "aws_region" {
  description = "The current AWS region"
  type        = string
}

variable "account_id" {
  description = "The current AWS account"
  type        = string
}

variable "api_name" {
  description = "The api name to be added to the base URL"
  type        = string
}
