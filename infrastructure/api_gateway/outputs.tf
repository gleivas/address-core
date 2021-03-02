output "this_api_gateway_id" {
  description = "The API gateway identifier"
  value       = aws_api_gateway_rest_api.this.id
}
