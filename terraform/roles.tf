resource "aws_iam_role" "OAuthAdministrator" {
  name               = "OAuthAdministrator"
  assume_role_policy = "${data.aws_iam_policy_document.auth0_assume_role_policy.json}"
}

resource "aws_iam_role_policy_attachment" "OAuthAdministrator" {
  role       = "${aws_iam_role.OAuthAdministrator.name}"
  policy_arn = "${aws_iam_policy.OAuthIdentity.arn}"

  # policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess" # for security reasons disabled
}

resource "aws_iam_role" "OAuthIdentity" {
  name               = "OAuthIdentity"
  assume_role_policy = "${data.aws_iam_policy_document.auth0_assume_role_policy.json}"
}

data "aws_iam_policy_document" "OAuthIdentity" {
  statement {
    actions   = ["sts:GetCallerIdentity"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "OAuthIdentity" {
  name        = "OAuthIdentity"
  description = "allows the caller to obtain its own identity"
  policy      = "${data.aws_iam_policy_document.OAuthIdentity.json}"
}

resource "aws_iam_role_policy_attachment" "OAuthIdentity" {
  role       = "${aws_iam_role.OAuthIdentity.name}"
  policy_arn = "${aws_iam_policy.OAuthIdentity.arn}"
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

resource "aws_iam_saml_provider" "auth0-provider" {
  name                   = "auth0-${replace(var.auth0_domain,".","-")}-provider"
  saml_metadata_document = "${data.local_file.auth0-saml-metadata.content}"
}
