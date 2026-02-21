module "network" {
  source      = "./modules/network"
  region      = var.region
  vpc_name    = var.vpc_name
  subnet_name = var.subnet_name
}

module "compute" {
  source     = "./modules/compute"
  zone       = var.zone
  network_id = module.network.network_id  
  subnet_id  = module.network.subnet_id   
}

module "database" {
  source      = "./modules/database"
  project_id  = var.project_id
  location_id = var.location_id
}