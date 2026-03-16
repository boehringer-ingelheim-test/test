terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    ec2            = var.localstack_endpoint
    s3             = var.localstack_endpoint
    iam            = var.localstack_endpoint
    sts            = var.localstack_endpoint
    dynamodb       = var.localstack_endpoint
  }
}

# ── VPC ──────────────────────────────────────────────────────────────────────
module "vpc" {
  source    = "../../modules/vpc"
  workspace = var.workspace
}

# ── S3 bucket ────────────────────────────────────────────────────────────────
module "s3" {
  source    = "../../modules/s3"
  workspace = var.workspace
  suffix    = "001"
}

# ── IAM role + instance profile ──────────────────────────────────────────────
module "iam" {
  source     = "../../modules/iam"
  workspace  = var.workspace
  bucket_arn = module.s3.bucket_arn
}

# ── EC2 instance ─────────────────────────────────────────────────────────────
module "ec2" {
  source               = "../../modules/ec2"
  workspace            = var.workspace
  instance_type        = var.instance_type
  disk_size_gb         = var.disk_size_gb
  subnet_id            = module.vpc.subnet_id
  security_group_id    = module.vpc.security_group_id
  iam_instance_profile = module.iam.instance_profile_name
}
