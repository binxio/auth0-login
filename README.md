# auth0-login
CLI to obtain JWT, SAML tokens, and AWS credentials using Auth0, OAuth and SAML.

## AWS access keys through Auth0 SAML support
[Auth0](https://auth0.com/docs/integrations/aws) can be configured as the identity provider for the AWS, allowing your Auth0 users
to directly log in to the AWS Console. Unfortunately, the functionality to obtain temporary access keys for calling AWS APIs and resources has been [deprecated
since June 8, 2017](https://auth0.com/docs/integrations/aws/tokens). With this command line utility, you can obtain AWS access keys through Auth0.

<!--more-->
For this utility to work, I assume you have already integrated Auth0 with AWS as described in the article ['Configure SSO with the AWS Console'](https://auth0.com/docs/integrations/aws/sso). If you have not done so, you can bootstrap yourself using  the [sample terraform configuration](https://github.com/binxio/auth0-login/tree/master/terraform) in this project.

## Add the application to Auth0
For the utility to work, add the auth0-login application as a Single Page Application to Auth0, and enable the SAML2 Web App addon. On the Settings tab, set the Application Callback URL to http://localhost:12200/saml and paste the following SAML configuration code into settings page:

```json
{
  "recipient": "https://signin.aws.amazon.com/saml",
  "audience": "https://signin.aws.amazon.com/saml",
  "mappings": {
    "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
  },
  "createUpnClaim": false,
  "passthroughClaimsWithNoMapping": false,
  "mapUnknownClaimsAsIs": false,
  "mapIdentities": false,
  "nameIdentifierFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
  "nameIdentifierProbes": [
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
  ]
}
```
This is identical to the AWS console configuration, with the exception of the type of application and the additional `recipient` field. This is to ensure that the 
SAML assertion has AWS as the recipient and not the callback `http://localhost:12200/saml`.

## configure auth0-login
Create a file ~/.saml-login with the following content:

```ini
[DEFAULT]
idp_url = https://<auth0-tenant>.auth0.com
client_id = <your-newly-added-client-id>
```

## configure AWS account aliases
Create a file ~/.aws-accounts with the following content:

```ini
[DEFAULT]
<aws-account-alias> = <aws-account-number>
```
This allows you to specify the AWS account by alias, which greatly improves readibility.

## Install auth0-login
To install the utility, type:

```bash
$ pip install auth0-login
```
## show all available AWS Roles
To show all available AWS roles. type:

```bash
$ saml-login aws-assume-role --show
[OAuthAdministrator@aws-alias]
idp_url = https://my-tenant.auth0.com
client_id = fJxw5Ir5E0eJDqdWkh+7VGI577uObvsFlAM0KZL5fI
aws_account = aws-alias
aws_role = OAuthAdministrator
aws_profile = OAuthAdministrator@aws-alias

[OAuthIdentity@aws-alias]
idp_url = https://my-tenant.auth0.com
client_id = fJxw5Ir5E0eJDqdWkh+7VGI577uObvsFlAM0KZL5fI
aws_account = aws-alias
aws_role = OAuthIdentity
aws_profile = OAuthIdentity@aws-alias
```
This will start the browser for authentication, and output all available roles in the form of the individual sections in the configuration file.
Add the desired roles to your `~/.saml-login`.

## obtaining AWS access keys
Now you can obtain the AWS access keys, by typing:
```bash
$ saml-login -c OAuthAdministrator@aws-alias aws-assume-role
INFO:Found credentials in shared credentials file: ~/.aws/credentials
INFO:credentials saved under AWS profile OAuthAdministrator@aws-alias
```
Again you will be prompted by the the browser for authentication: the access keys are stored in `~/.aws/credentials`. 

## Conclusion
With the command line utility, you can have SSO *and* temporary access keys for AWS using Auth0!
