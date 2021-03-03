provider "aws" {
  version = "~> 2.0"
  region  = "us-east-1"
}

terraform {
  required_version = "0.12.29"

  backend "s3" {
    bucket  = "betbots-terraform-state"
    key     = "address_core/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id    = data.aws_caller_identity.current.account_id
  aws_region    = data.aws_region.current.name
  service       = "address-core"
  prefix        = "${local.service}-${terraform.workspace}"
}

module "address_endpoint" {
  source         = "./lambda"
  service        = local.service
  function_name  = "address_endpoint"
  lambda_handler = "address_core.endpoints.AddressApiHandler"
  source_files   = ["address_core"]
  requirements   = "requirements/base.txt"
  env_vars = {
    precisely_api_key    = aws_ssm_parameter.precisely_api_key.name
    precisely_api_secret = aws_ssm_parameter.precisely_api_secret.name
  }
  additional_policies = [
    aws_iam_policy.access_secrets_policy.arn
  ]
}

### API GATEWAY ###
module "api_gateway" {
  source      = "./api_gateway"
  service     = local.service
  api_version = "v1"
  aws_region  = local.aws_region
  account_id  = local.account_id
  lambda_arn  = module.address_endpoint.this_lambda_function_arn
  api_name    = "address"
}


### SSM ###
resource "aws_iam_policy" "access_secrets_policy" {
  name        = "${local.prefix}-secrets_access"
  path        = "/"
  description = "IAM policy for accessing the certificate"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParameter"],
      "Resource": "arn:aws:ssm:${local.aws_region}:${local.account_id}:parameter/${local.prefix}/*"
    }
  ]
}
EOF
}

resource "aws_ssm_parameter" "precisely_api_key" {
  name  = "/${local.prefix}/api_key"
  type  = "SecureString"
  value = "TEMPORARY VALUE"
  lifecycle {
    ignore_changes = ["value"]
  }
  tags = {
    env     = terraform.workspace
    service = local.service
  }
}

resource "aws_ssm_parameter" "precisely_api_secret" {
  name  = "/${local.prefix}/api_secret"
  type  = "SecureString"
  value = "TEMPORARY VALUE"
  lifecycle {
    ignore_changes = ["value"]
  }
  tags = {
    env     = terraform.workspace
    service = local.service
  }
}
