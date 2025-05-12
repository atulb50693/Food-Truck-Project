terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "eu-west-2"
}

variable "DB_USER" {
  type=string
}

variable "DB_PASSWORD" {
  type=string
}

variable "DB_NAME" {
  type=string
}

variable "DB_PORT" {
  type=string
}

variable "DB_HOST" {
  type=string
}

variable "aws_access_key_id" {
  type=string
}

variable "aws_secret_access_key" {
  type=string
}

data "aws_ecr_image" "service_image" {
  repository_name = "c16-tul-abuelhia-pipeline"
  image_tag       = "latest"
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "task" {
    family = "c16-tul-abuelhia-pipeline"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu = 512
    memory = 1024
    execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
    container_definitions = jsonencode([{
        name      = "c16-tul-abuelhia-pipeline"
        image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-tul-abuelhia-pipeline:latest"
        essential = true
        command = ["python3", "pipeline.py"]
        environment = [
            {
                name = "DB_HOST"
                value = var.DB_HOST
            },
            {
                name = "DB_NAME"
                value = var.DB_NAME
            },
            {
                name = "DB_USER"
                value = var.DB_USER
            },
            {
                name = "DB_PASSWORD"
                value = var.DB_PASSWORD
            },
            {
                name = "DB_PORT"
                value = var.DB_PORT
            },
            {
                name = "aws_secret_access_key"
                value = var.aws_secret_access_key
            },
            {
                name = "aws_access_key_id"
                value = var.aws_access_key_id
            }]
        portMappings = [
            {
            containerPort = 3306
            hostPort      = 3306
            }
        ]
        logConfiguration = {
            logDriver = "awslogs",
            options = {
                awslogs-group = "ecs/c16-tul-abuelhia-pipeline",
                awslogs-region = "eu-west-2",
                awslogs-stream-prefix = "ecs"
                }
            }
        }
    ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}
