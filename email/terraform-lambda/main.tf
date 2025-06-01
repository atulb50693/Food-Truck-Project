terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "eu-west-2"
}

data "aws_ecr_image" "c16-ta-lambda" {
  repository_name = "c16-ta-lambda"
  image_tag       = "latest"
}


data "aws_iam_policy_document" "assume_role" {
  # trust policy for lambda to assume a role
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  # setting up iam role for lambda
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "lambda_logging" {
  # creates policy document with set of permissions for lambda logging
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging" {
  # permissions policy for lambda logging using the policy document/statement
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  # attaching the permissions policy to the role assumed before
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_cloudwatch_log_group" "c16-ta-email-report-lg" {
  name              = "/aws/lambda/c16-ta-email-report"
  retention_in_days = 14
}

resource "aws_lambda_function" "c16-ta-email-report-lambda" {
    image_uri = data.aws_ecr_image.c16-ta-lambda.image_uri
    function_name = "c16-tul-abuelhia-email-report"
    role          = aws_iam_role.iam_for_lambda.arn
    package_type = "Image"
    handler       = "report_data.handler"
    runtime = "python3.12"
    
    environment {
        variables = {
            DB_HOST = var.DB_HOST,
            DB_NAME = var.DB_NAME,
            DB_USER = var.DB_USER,
            DB_PASSWORD = var.DB_PASSWORD,
            DB_PORT = var.DB_PORT,
            aws_access_key_id = var.aws_access_key_id,
            aws_secret_access_key = var.aws_secret_access_key
        }
    }

    logging_config {
        log_format = "Text"
        log_group = aws_cloudwatch_log_group.c16-ta-email-report-lg.name
    }
    
    depends_on = [
        aws_iam_role_policy_attachment.lambda_logs,
        aws_cloudwatch_log_group.c16-ta-email-report-lg,
    ]
}

