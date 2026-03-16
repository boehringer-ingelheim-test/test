variable "workspace" {
  description = "Workspace / project name"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type (driven by t-shirt size)"
  type        = string
  default     = "t3.medium"
}

variable "disk_size_gb" {
  description = "Root volume size in GB"
  type        = number
  default     = 50
}

variable "subnet_id" {
  description = "Subnet ID to launch the instance into"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID to attach"
  type        = string
}

variable "iam_instance_profile" {
  description = "IAM instance profile name"
  type        = string
}
