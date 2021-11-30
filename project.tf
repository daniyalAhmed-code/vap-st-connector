module "api_project" {
  source = "./vendor/modules/api"
  # stage_name   = var.env
  stage_name = "beta"
  #name         = "${var.name}-${var.env}-device-type"
  name           = "Project"
  description    = "API for Activity Outbound Resource"
  swagger_file   = "./templates/swagger-Project-1.0.0.yaml"
  common_swagger = "./templates/common.yaml"
  waf_acl_id     = data.terraform_remote_state.infra.outputs.regional_waf_id
  swagger_vars = {
    REGION                 = data.aws_region.current.name
    DEVICE_TYPE_LAMBDA_ARN = module.device_type_lambda.lambda_function_arn
    EXECUTION_ROLE_ARN     = module.lambda_execution_role.iam_role_arn
    AUTHORIZER_LAMBDA_URI  = data.terraform_remote_state.api.outputs.lambda_authorizer_invoke_arn
  }
  add_lambda_permission = false
  domain_name           = data.terraform_remote_state.api.outputs.api_gateway_custom_domain_name
  base_path             = "project"
}
