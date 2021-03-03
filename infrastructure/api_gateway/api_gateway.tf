data "template_file" api_swagger {
  template = file("${path.root}/swagger.yaml")

  vars = {
    aws_region          = var.aws_region
    lambda_endpoint_arn = var.lambda_arn
    api_name            = "${var.service}-${terraform.workspace}"
  }
}

resource "aws_api_gateway_api_key" "this" {
  name = "address-${terraform.workspace}-demo-api-key"
}

resource "aws_api_gateway_rest_api" "this" {
  name = "${var.service}-${terraform.workspace}"
  body = data.template_file.api_swagger.rendered

  endpoint_configuration {
    types = ["EDGE"]
  }
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = var.api_version

  variables = {
    hash = md5(data.template_file.api_swagger.rendered)
  }
}

resource "aws_api_gateway_usage_plan" "this" {
  name = "my_usage_plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.this.id
    stage  = aws_api_gateway_deployment.this.stage_name
  }
}

resource "aws_api_gateway_usage_plan_key" "this" {
  key_id        = aws_api_gateway_api_key.this.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.this.id
}

resource "aws_lambda_permission" "api_gateway_invocation" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${var.account_id}:${aws_api_gateway_rest_api.this.id}/*/*"
}
