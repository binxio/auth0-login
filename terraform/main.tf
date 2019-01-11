resource "auth0_client" "oauth-cli" {
  name        = "oauth-cli"
  description = "CLI for obtaining JWT and SAML access tokens"
  app_type    = "native"

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

  script = <<EOF
function (user, context, callback) {

  user.awsRole = '${aws_iam_role.administrator.arn},${aws_iam_saml_provider.auth0-provider.arn}';
  user.awsRoleSession = 'admin';

  context.samlConfiguration.mappings = {
    'https://aws.amazon.com/SAML/Attributes/Role': 'awsRole',
    'https://aws.amazon.com/SAML/Attributes/RoleSessionName': 'awsRoleSession'
  };

  callback(null, user, context);
}
EOF

  enabled = true
}

data "http" "auth0-saml-metadata" {
  url = "https://${var.auth0_domain}/samlp/metadata/${auth0_client.oauth-cli.client_id}"

  request_headers {
    "Accept" = "application/xml"
  }
}

output "oauth-cli.ini" {
  value = "\n\n[${var.auth0_domain}]\nidp_url = https://${var.auth0_domain}\nclient_id = ${auth0_client.oauth-cli.client_id}\n"
}
