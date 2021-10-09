variable "aws_region" {
    type = string
    default = "us-east-1"
}

variable "availability_zone_names" {
    type = list(string)
    default = ["us-east-1a", "us-east-1b"]  
}

variable "container_image" {
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