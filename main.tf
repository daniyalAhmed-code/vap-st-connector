#################
#### IAM ####
#################
module "policy_invoke_lambda" {
  source      = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version     = "4.5.0"
  name        = "${var.name}-api-gateway-lambda-policy"
  path        = "/"
  description = "Policy to invoke lambda"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "lambda:invokeFunction"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

module "lambda_execution_role" {
  source            = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version           = "4.5.0"
  create_role       = true
  role_name         = "${var.name}-apigateway-lambda-execution-role"
  role_requires_mfa = false
  trusted_role_services = [
    "apigateway.amazonaws.com"
  ]
  custom_role_policy_arns = [
    module.policy_invoke_lambda.arn
  ]
  number_of_custom_role_policy_arns = 1
}

#################
#### Lambdas ####
#################
# TODO : Lambda 3.9 Docker Image Not publish yet
# https://hub.docker.com/r/lambci/lambda/tags?page=1&ordering=last_updated
# ISSUE: https://github.com/lambci/lambci/issues/138
# PR: https://github.com/lambci/lambci/pull/139
module "simple_salesforce_lambda_layer" {
  source              = "./vendor/lambda"
  create_function     = false
  create_layer        = true
  layer_name          = "simple-salesforce-lambda-layer"
  description         = "Lambda layer with Simple Salesforce library"
  runtime             = var.lambda_runtime
  compatible_runtimes = var.layer_compatible_runtimes
  source_path = {
    pip_requirements = "lambdas/layers/simple-salesforce/requirements.txt",
    prefix_in_zip    = "python"
  }
  hash_extra      = sha256(file("lambdas/layers/simple-salesforce/requirements.txt"))
  build_in_docker = true
}

module "utils_lambda_layer" {
  source              = "./vendor/lambda"
  create_function     = false
  create_layer        = true
  layer_name          = "utils-lambda-layer"
  description         = "Lambda layer with some util modules"
  compatible_runtimes = var.layer_compatible_runtimes
  source_path = {
    path             = "${path.module}/lambdas/layers/utils",
    pip_requirements = false
    prefix_in_zip    = "python/utils"
  }
  build_in_docker = true
}

########################
#### API Usage Plan ####
########################
module "api_usage_plan" {
  depends_on = [
    module.api_device_type
  ]
  source      = "./vendor/modules/api-usage-plan"
  name        = "${var.name}-${var.env}-st-usage-plan-01"
  description = "SiteTracker Endpoint API Usage PLAN"
  apis = [
    {
      id    = module.api_device_type.id
      stage = module.api_device_type.stage
    },
    {
      id    = module.api_activity.id
      stage = module.api_activity.stage
    },
    {
      id    = module.api_activity_outbound.id
      stage = module.api_activity_outbound.stage
    },
    {
      id    = module.api_project.id
      stage = module.api_project.stage
    },
    {
      id    = module.api_project_outbound.id
      stage = module.api_project_outbound.stage
    }
  ]
}