terraform {

  required_version = "> 0.15.4"
  //    required_version = "~> 1.0.6"

  backend "s3" {
    bucket                      = "vap-aws-terraform-remote-state-centralized"
    key                         = "vap-st-connector/eu-central-1/{{ENV}}/terraform.tfstate"
    region                      = "eu-central-1"
    encrypt                     = true
    dynamodb_table              = "vap-aws-terraform-locks-centralized"
    acl                         = "private"
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_metadata_api_check     = true
    kms_key_id                  = "arn:aws:kms:eu-central-1:793073444497:key/b9b5b5e7-156b-49f9-8e28-cec7e9c4fbca"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.58.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"

  assume_role {
    role_arn = var.DEPLOY_ROLE
  }

  default_tags {
    tags = {
      Environment     = "{{ENV}}"
      ManagedBy       = "cloud.automation@outscope.com"
      DeployedBy      = "terraform"
      Project         = "vap"
      Confidentiality = "c3"
      TaggingVersion  = "v2.3"
    }
  }

  skip_get_ec2_platforms      = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}