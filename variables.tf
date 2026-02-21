variable "project_id" {
    description = "The ID of the GCP project"
    type        = string
}

variable "region" {
    description = "The GCP region"
    type        = string
}

variable "zone" {
    description = "The GCP zone"
    type        = string
}

variable "location_id" {
    description = "The GCP location ID"
    type        = string
}

variable "vpc_name" {
    description = "The name of the VPC"
    type        = string
}

variable "subnet_name" {
    description = "The name of the subnet"
    type        = string
}