from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:////data/provisioner.db"

    # LocalStack
    localstack_endpoint: str = "http://localstack:4566"
    aws_region: str = "eu-west-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"

    # Terraform state (stored in LocalStack S3)
    terraform_state_bucket: str = "tf-state-provisioner"
    terraform_state_dynamodb_table: str = "terraform-lock"
    terraform_working_dir: str = "/app/terraform/environments/dev"

    class Config:
        env_file = ".env"


settings = Settings()
