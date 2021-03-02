data "template_file" api_swagger {
  template = file("${path.root}/swagger.yaml")

  vars = {
    aws_region          = var.aws_region
    lambda_endpoint_arn = var.lambda_arn
    api_name            = "${var.service}-${terraform.workspace}"
  }
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

resource "aws_lambda_permission" "api_gateway_invocation" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${var.account_id}:${aws_api_gateway_rest_api.this.id}/*/*"
}
