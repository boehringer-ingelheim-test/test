terraform {
  backend "s3" {
    bucket                      = "tf-state-provisioner"
    key                         = "dev/terraform.tfstate"
    region                      = "eu-west-1"
    endpoint                    = "http://localstack:4566"
    access_key                  = "test"
    secret_key                  = "test"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true

    # DynamoDB lock table (also on LocalStack)
    dynamodb_table              = "terraform-lock"
    dynamodb_endpoint           = "http://localstack:4566"
  }
}
