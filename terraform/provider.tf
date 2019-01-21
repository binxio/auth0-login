provider "aws" {
  profile = "${var.aws_profile}"
  region  = "${var.aws_region}"
}

data "aws_caller_identity" "current" {}
data "aws_iam_account_alias" "current" {}

provider "auth0" {
  domain        = "${var.auth0_domain}"
  client_id     = "${var.auth0_client_id}"
  client_secret = "${var.auth0_client_secret}"
}
