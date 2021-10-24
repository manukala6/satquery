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

data "aws_ecr_repository" "api_ecr" {
  name = var.ecr_name
}

data "aws_vpc" "core_vpc" {
  id = var.vpc_id
}

data "aws_internet_gateway" "core_igw" {
  filter {
    name = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}

module "subnets" {
  source = "cloudposse/dynamic-subnets/aws"
  version = "0.39.4"
  namespace = "geonos"
  stage = "dev"
  name = "satquery-api"
  vpc_id = var.vpc_id
  igw_id = data.aws_internet_gateway.core_igw.id
  cidr_block = data.aws_vpc.core_vpc.cidr_block
  availability_zones = ["us-east-1a", "us-east-1b"]
  vpc_default_route_table_id = var.mongodb_route_table_id
}

module "security_group" {
  source = "terraform-aws-modules/security-group/aws//modules/http-80"

  name = "satquery-api-sg"
  vpc_id = var.vpc_id
  ingress_cidr_blocks = ["0.0.0.0/0"]
}

module "alb" {
  source = "terraform-aws-modules/alb/aws"
  version = "~> 6.0"

  name = var.elb_name
  vpc_id = module.security_group.security_group_vpc_id
  subnets = module.subnets.public_subnet_ids
  security_groups = [module.security_group.security_group_id]

  target_groups = [
    {
      name = var.tg_name
      backend_port = 80
      backend_protocol = "HTTP"
      target_type = "ip"
      vpc_id = var.vpc_id
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

data "aws_ecs_cluster" "cluster" {
  cluster_name = "satquery-api-cluster"
}

module "container_definition" {
  source = "cloudposse/ecs-container-definition/aws"
  version = "0.58.1"

  container_name = "satquery-api-container"
  container_image = var.container_image
  
  port_mappings = [
    {
      containerPort = 80
      hostPort = 80
      protocol = "tcp"
    }
  ]

  log_configuration = var.awslogs_configuration

  environment = [
    {
      name = "MONGODB_DEV_URL"
      value = var.mongodb_connection_str
    }
  ]
}

module "ecs-alb-service-task" {
  source  = "cloudposse/ecs-alb-service-task/aws"
  version = "0.58.0"

  namespace = "geonos"
  stage = "dev"
  name = var.branch_name
  container_definition_json = module.container_definition.json_map_encoded_list
  ecs_cluster_arn = data.aws_ecs_cluster.cluster.arn
  launch_type = "FARGATE"
  vpc_id = var.vpc_id
  security_groups = [module.security_group.security_group_id]
  subnet_ids = module.subnets.public_subnet_ids
  task_exec_policy_arns = var.fargate_task_exec_policy
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