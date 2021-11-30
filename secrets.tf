#################
#### Secrets ####
#################
module "vdp_pt_secret" {
  source                  = "./modules/secrets"
  name                    = "/credentials/sitetracker/Portugal/Vodafone"
  description             = "Secret with Site Tracker Credentials To VDF PT Mno in Portugal"
  kms_key_id              = data.terraform_remote_state.infra.outputs.kms_key_id
  recovery_window_in_days = var.secrets_recovery_window_in_days
  value = jsonencode({
    username : "changeme",
    password : "changeme",
    security_token : "changeme",
    client_id : "changeme",
    client_secret : "changeme",
    domain : "changeme"
  })
}
