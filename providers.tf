terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "tf-backend-2305"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region     
  zone    = var.zone       
}