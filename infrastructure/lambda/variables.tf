variable "service" {
  description = "The name of the service"
  type        = string
}

variable "function_name" {
  description = "The lambda function name"
  type        = string
}

variable "lambda_handler" {
  description = "The lambda function entrypoint"
  type        = string
}

variable "runtime" {
  description = "The lambda function runtime"
  type        = string
  default     = "python3.7"
}

variable "log_retention" {
  description = "The log retention period in days"
  type        = string
  default     = 7
}

variable "source_files" {
  description = "The lambda function source files"
  type        = list(string)
}

variable "requirements" {
  description = "The lambda function requirements file"
  type        = string
}

variable "memory_size" {
  description = "The memory configuration of the lambda function"
  type        = number
  default     = 128
}

variable "timeout" {
  description = "The lambda function timeout in seconds"
  type        = number
  default     = 15
}

variable "env_vars" {
  description = "Environment variables passed to the lambda function"
  type        = map
}

variable "additional_policies" {
  description = "Additional policies ARN to be attached to the lambda function"
  type        = list(string)
}
