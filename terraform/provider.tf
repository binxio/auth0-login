provider "aws" {
  profile = "${var.aws_profile}"
  region  = "${var.aws_region}"
}

provider "auth0" {
  domain        = "${var.auth0_domain}"
  client_id     = "${var.auth0_client_id}"
  client_secret = "${var.auth0_client_secret}"
}
