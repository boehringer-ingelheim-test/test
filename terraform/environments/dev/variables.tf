variable "workspace" {
  description = "Workspace / project name (set per provisioning request)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "localstack_endpoint" {
  description = "LocalStack endpoint URL"
  type        = string
  default     = "http://localstack:4566"
}

variable "instance_type" {
  description = "EC2 instance type (driven by t-shirt size)"
  type        = string
  default     = "t3.medium"
}

variable "disk_size_gb" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}
