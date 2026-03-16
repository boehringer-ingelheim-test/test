variable "workspace" {
  description = "Workspace / project name"
  type        = string
}

variable "suffix" {
  description = "Random suffix to ensure bucket name uniqueness"
  type        = string
  default     = "001"
}
