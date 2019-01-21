## terraform configuration
To setup your Auth0 SSO configuration with AWS, you can use [Terraform](https://www.terraform.io/downloads.html).


## Install Terraform

Install terraform 0.11.x on your machine.

## Install the Auth0 terraform provider

[Yieldr](https://www.yieldr.com/) created an [Auth0 terraform provider](https://github.com/yieldr/terraform-provider-auth0). It  isn't listed in the official Terraform repository, so you have to download the [binary](https://github.com/yieldr/terraform-provider-auth0/releases) and place in the directory ~/.terraform/plugins.

## Configure the Auth0 API Explorer client
For the provider to be able to use the Auth0 Management API, you need to install the Auth0 API Explorer client in Auth0. Check if you have already 
created it, in the Auth0 application list. If not, follow the instructions at [authorize a Machine-to-Machine Application for the Management API](https://auth0.com/docs/api/management/v2/create-m2m-app). Note the `client_id` and `client_secret`.

## set terraform variables

create a file, my.tfvars with the following content:

```
aws_profile = "<your-aws-profile>"
auth0_domain = "<your-auth0-tenant-name>.auth0.com"
auth0_client_id = "<api explorer client id>"
auth0_client_secret = "<api explorer client secret>"
```

## run terraform
To provision SSO, type:

```
$ terraform init
$ terraform apply -var-file=my.tfvars
```

## note
This configuration creates an OAuthAdministrator and OAuthIdentity Role.  The configuration  assigns both roles to every authenticated user in Auth0.
You may want to tailor the rule to explicitly authorize specific users. As a precaution, both roles only have to
permission 'sts:GetCallerIdentity'.
