resource "auth0_client" "auth0-cli" {
  name        = "auth0-login"
  description = "CLI for obtaining JWT and SAML access tokens"
  app_type    = "spa"

  grant_types = [
    "authorization_code",
    "implicit",
    "refresh_token",
  ]

  is_token_endpoint_ip_header_trusted = false
  is_first_party                      = true
  oidc_conformant                     = true
  sso_disabled                        = false
  cross_origin_auth                   = false
  logo_uri                            = ""
  sso                                 = true

  callbacks = [
    "http://localhost:12200/saml",
    "http://localhost:12200/callback",
    "https://signin.aws.amazon.com/saml",
  ]

  addons = {
    samlp = {
      recipient = "https://signin.aws.amazon.com/saml"
      audience  = "https://signin.aws.amazon.com/saml"

      mappings = {
        email = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
        name  = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
      }

      create_upn_claim                   = false
      passthrough_claims_with_no_mapping = false
      map_unknown_claims_as_is           = false
      map_identities                     = false
      name_identifier_format             = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"

      name_identifier_probes = [
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
      ]
    }
  }

  jwt_configuration = {
    alg                 = "RS256"
    lifetime_in_seconds = 36000
    secret_encoded      = false
  }

  custom_login_page_on = true
}

resource "auth0_rule" "grant-admin" {
  name = "grant aws admin role to all from ${var.aws_profile}"

  /* Note, this script grants both roles to everybody. You may want to grant roles
               based on group memberships or role. */
  script = <<EOF
function (user, context, callback) {

  user.awsRole = [ '${aws_iam_role.OAuthAdministrator.arn},${aws_iam_saml_provider.auth0-provider.arn}', 
		   '${aws_iam_role.OAuthIdentity.arn},${aws_iam_saml_provider.auth0-provider.arn}'];
  user.awsRoleSession = user.email;

  context.samlConfiguration.mappings = {
    'https://aws.amazon.com/SAML/Attributes/Role': 'awsRole',
    'https://aws.amazon.com/SAML/Attributes/RoleSessionName': 'awsRoleSession'
  };

  callback(null, user, context);
}
EOF

  enabled = true
}

/* fixed in PR https://github.com/terraform-providers/terraform-provider-http/pull/16
data "http" "auth0-saml-metadata" {
  url = "https://${var.auth0_domain}/samlp/metadata/${auth0_client.auth0-cli.client_id}"

  request_headers {
    "Accept" = "application/xml"
  }
}
*/

data "local_file" "auth0-saml-metadata" {
  filename   = ".saml-metadata.xml"
  depends_on = ["null_resource.auth0-saml-metadata"]
}

resource "null_resource" "auth0-saml-metadata" {
  provisioner "local-exec" {
    command = "curl -L -sS --fail -o .saml-metadata.xml https://${var.auth0_domain}/samlp/metadata/${auth0_client.auth0-cli.client_id}"
  }
}

output ".saml-login" {
  value = <<EOF
[DEFAULT]
idp_url = https://${var.auth0_domain}
client_id = ${auth0_client.auth0-cli.client_id}

[administrator@${data.aws_iam_account_alias.current.account_alias}]
idp_url = https://${var.auth0_domain}
client_id = ${auth0_client.auth0-cli.client_id}
aws_profile = administrator@${data.aws_iam_account_alias.current.account_alias}
aws_role = OAuthAdministrator
aws_account = ${data.aws_iam_account_alias.current.account_alias}

[identity@${data.aws_iam_account_alias.current.account_alias}]
idp_url = https://${var.auth0_domain}
client_id = ${auth0_client.auth0-cli.client_id}
aws_profile = identity@${data.aws_iam_account_alias.current.account_alias}
aws_role = OAuthIdentity
aws_account = ${data.aws_iam_account_alias.current.account_alias}

EOF
}

output ".aws-accounts" {
  value = <<EOF
[DEFAULT]
${data.aws_iam_account_alias.current.account_alias} = ${data.aws_caller_identity.current.account_id}
EOF
}
