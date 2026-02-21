#COMPUTE ENGINE VM
resource "google_compute_instance" "free_vm" {
  name         = "my-free-tier-vm"
  machine_type = "e2-micro"
  zone         = var.zone

  tags = ["allow-ssh"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 30 
      type  = "pd-standard"
    }
  }

  network_interface {
    network    = var.network_id
    subnetwork = var.subnet_id
    access_config {} 
  }
}