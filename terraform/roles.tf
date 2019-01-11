resource "aws_iam_saml_provider" "auth0-provider" {
  name                   = "auth0-${replace(var.auth0_domain,".","-")}-provider"
  saml_metadata_document = "${data.http.auth0-saml-metadata.body}"
}

resource "aws_iam_role" "administrator" {
  name               = "OAuthAdministrator"
  assume_role_policy = "${data.aws_iam_policy_document.auth0_assume_role_policy.json}"
}

resource "aws_iam_policy_attachment" "PowerUserAccess" {
  name       = "PowerUserAccess"
  roles      = ["${aws_iam_role.administrator.name}"]
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

data "aws_iam_policy_document" "auth0_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithSAML"]

    condition {
      test     = "StringEquals"
      variable = "SAML:aud"
      values   = ["https://signin.aws.amazon.com/saml"]
    }

    principals {
      type        = "Federated"
      identifiers = ["${aws_iam_saml_provider.auth0-provider.arn}"]
    }
  }
}
