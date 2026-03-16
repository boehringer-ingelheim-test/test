variable "workspace" {
  description = "Workspace / project name"
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket this role is allowed to access"
  type        = string
}
