# Terraform Remote State
data "terraform_remote_state" "infra" {
  backend = "s3"
  config = {
    bucket = "vap-aws-terraform-remote-state-centralized"
    key    = "vap-platform-infra/${var.region}/${var.env}/terraform.tfstate"
    region = var.region
  }
}


data "terraform_remote_state" "api" {
  backend = "s3"
  config = {
    bucket = "vap-aws-terraform-remote-state-centralized"
    key    = "vap-api/${var.region}/${var.env}/terraform.tfstate"
    region = var.region
  }
}


data "aws_region" "current" {}