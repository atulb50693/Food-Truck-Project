# Folder for the email script and related scripts

Contains sub-folders:

* `terraform-lambda/`
* `report_data/`

# Terraform

`terraform-lambda/` - contains code for deployment of the daily email infrastructure.

* `main.tf`

    * Utilises an existing ECR repository to upload the `report_data.py` file as a lambda docker image
    * Creates a CloudWatch log group for the AWS Lambda resource
    * Sets up the IAM roles for the AWS Lambda resource
    

* `variables.tf` 

    * allows for environmental variables to be passed into the main file.


Please setup a third file, `terraform.tfvars`, that specifies environmental variables and follows this format:

```
DB_USER=<your_database_username>
DB_PASSWORD=<your_database_password>
DB_PORT=5432
DB_NAME=<your_database_name>
DB_HOST=<your_database_address>
aws_access_key_id=<your_aws_access_key>
aws_secret_access_key=<your_aws_secret_access_key>
```


This configuration assumes that AWS CLI has been set up and so the AWS keys are not required to run the `main.tf` file. If you haven't set up the AWS CLI, you can follow up to step 3 from this [article](https://medium.com/@simonazhangzy/installing-and-configuring-the-aws-cli-7d33796e4a7c) to help you.

## Get started

The Terraform files can be run using the following steps for the first time:

1. Run `terraform init`

2. Set up a new ECR image repository on your AWS account and change the repository name in `main.tf` to the name of the newly created ECR repository.

3. Carry out the steps within the ['Get Started'](#get-started-1) section below to add a Docker image to the ECR repository that have been created in step 2.

5. Run `terraform apply` once complete to apply the rest of script.

Once the ECR repository has been set up with a Docker image, only step 5 is required to set up the infrastructure from now on.


# Email Report 

`report_data/` - Contains a Dockerfile required for setting up a lambda Docker image of the `report_data.py` file.

* `Dockerfile` - which includes the commands required to convert the lambda function script into a Docker image

* `report_data.py` - which is the lambda script to be converted into a Docker image.

* `report_data_2025-03-25.html` - which is an example email using data in the form of a html file.

* `report_data_2025-03-25.json` - which is example data used within an email in JSON format.


## IMPORTANT

- NOTE: YOUR ACCOUNT MUST BE EXITED FROM SANDBOX MODE IN ORDER TO SEND EMAILS THAT ARE NOT VERIFIED ON YOUR AWS. TO EXIT SANDBOX FOLLOW: https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html?icmpid=docs_ses_console 


## Get started <a name="dockerise_image"></a>

To set up the ECR repository with the lambda Docker image, carry out the following steps after carrying out steps 1 and 2 from the terraform section:


1. Set up a .env of format:

```
DB_USER=
DB_PASSWORD=
DB_PORT=
DB_NAME=
DB_HOST=
```

2. Follow the steps on [here](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions) to dockerise the python script, making sure to use the ` --env-file .env` flag for docker build.

3. Follow the push commands on the AWS console for the relevant ECR repository

