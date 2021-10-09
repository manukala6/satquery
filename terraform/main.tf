terraform {
  required_providers {
      aws = {
          source = "hashicorp/aws"
          version: "~> 3.0"
      }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_ecr_repository" "api_ecr" {
  name = "satquery-api-dev"
}

resource "aws_vpc" "geonos_vpc" {
  cidr_block = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "geonos_vpc"
  }
}

resource "aws_internet_gateway" "geonos_igw" {
  vpc_id = resource.aws_vpc.geonos_vpc.id

  tags = {
    Name = "geonos_igw"
  }
}

module "subnets" {
  source = "cloudposse/dynamic-subnets/aws"
  version = "0.39.4"
  namespace = "geonos"
  stage = "dev"
  name = "satquery-api"
  vpc_id = resource.aws_vpc.geonos_vpc.id
  igw_id = resource.aws_internet_gateway.geonos_igw.id
  cidr_block = resource.aws_vpc.geonos_vpc.cidr_block
  availability_zones = ["us-east-1a", "us-east-1b"]
}

module "security_group" {
  source = "terraform-aws-modules/security-group/aws//modules/http-80"

  name = "satquery-api-sg"
  vpc_id = resource.aws_vpc.geonos_vpc.id
  ingress_cidr_blocks = ["0.0.0.0/0"]
}

module "alb" {
  source = "terraform-aws-modules/alb/aws"
  version = "~> 6.0"

  name = "satquery-api-alb"
  vpc_id = module.security_group.security_group_vpc_id
  subnets = module.subnets.public_subnet_ids
  security_groups = [module.security_group.security_group_id]

  target_groups = [
    {
      name = "satquery-api-tg"
      backend_port = 80
      backend_protocol = "HTTP"
      target_type = "ip"
      vpc_id = resource.aws_vpc.geonos_vpc.id
      health_check = {
        path = "/docs"
        port = "80"
        matcher = "200-399"
        protocol = "HTTP"
      }
    }
  ]

  http_tcp_listeners = [
    {
      port = 80
      protocol = "HTTP"
      target_group_index = 0
    }
  ]
}

resource "aws_ecs_cluster" "cluster" {
  name = "satquery-api-cluster"
}

module "container_definition" {
  source = "cloudposse/ecs-container-definition/aws"
  version = "0.58.1"

  container_name = "satquery-api-container"
  container_image = "754370150126.dkr.ecr.us-east-1.amazonaws.com/geonos-dev:latest"
  port_mappings = [
    {
      containerPort = 80
      hostPort = 80
      protocol = "tcp"
    }
  ]
}

module "ecs-alb-service-task" {
  source  = "cloudposse/ecs-alb-service-task/aws"
  version = "0.58.0"

  namespace = "geonos"
  stage = "dev"
  name = "satquery-api"
  container_definition_json = module.container_definition.json_map_encoded_list
  ecs_cluster_arn = aws_ecs_cluster.cluster.arn
  launch_type = "FARGATE"
  vpc_id = resource.aws_vpc.geonos_vpc.id
  security_groups = [module.security_group.security_group_id]
  subnet_ids = module.subnets.public_subnet_ids
  task_exec_policy_arns = ["arn:aws:iam::754370150126:policy/fargate_default_role"]
  assign_public_ip = true

  health_check_grace_period_seconds = 60
  ignore_changes_task_definition = false

  ecs_load_balancers = [
    {
      target_group_arn = module.alb.target_group_arns[0]
      elb_name = ""
      container_name = "satquery-api-container"
      container_port = 80
    }
  ]
}