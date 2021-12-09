variable "aws_region" {
    type = string
    default = "us-east-1"
}

variable "availability_zone_names" {
    type = list(string)
    default = ["us-east-1a", "us-east-1b"]  
}

variable "container_image" {
}

variable "vpc_id" {
    type = string
}

variable "container_ports" {
    type = list(object({
        containerPort = number
        hostPort = number
        protocol = string
    }))
    default = [
        {
            containerPort = 80
            hostPort = 80
            protocol = "tcp"
        }
    ]
  
}

variable "fargate_task_exec_policy" {
    type = list(string)
}

variable "ecr_name" {
    type = string
}

variable "elb_name" {
    type = string  
}

variable "tg_name" {
    type = string
}

variable "branch_name" {
    type = string
}

variable "mongodb_route_table_id" {
    type = string
}

variable "mongodb_connection_str" {
    type = string
}

variable "awslogs_configuration" {
    type = object({
        logDriver = string
        options = object({
            awslogs-group = string
            awslogs-region = string
            awslogs-stream-prefix = string
        })
    })
}

variable "aws_access_key_id" {
    type = string
}

variable "aws_secret_access_key" {
    type = string
}
