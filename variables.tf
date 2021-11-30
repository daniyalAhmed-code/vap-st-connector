variable "name" {
  type    = string
  default = "vap-st"
}

variable "DEPLOY_ROLE" {
  type        = string
  description = "AWS IAM ARN role to deploy"
}

variable "env" {
  type        = string
  description = "Platform Environment"
  default     = "test"
}

variable "lambda_runtime" {
  type        = string
  description = "Lambda Runtime"
  default     = "python3.8"
}

variable "layer_compatible_runtimes" {
  type        = list(string)
  description = "List of Runtimes this layer is compatible with"
  default     = ["python3.8"]
}

variable "logs_retention_days" {
  type    = number
  default = 30
}

variable "secrets_recovery_window_in_days" {
  description = " (Optional) Specifies the number of days that AWS Secrets Manager waits before it can delete the secret. This value can be 0 to force deletion without recovery or range from 7 to 30 days. The default value is 30"
  type        = number
  default     = 30
}

variable "region" {
  type    = string
  default = "eu-central-1"
}
