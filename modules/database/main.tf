# RANDOM 4 CHAR HEX STRING
resource "random_id" "db_suffix" {
  byte_length = 2
}

#FIRESTORE DB
resource "google_firestore_database" "default_db" {
  project     = var.project_id
  name        = "tf-code-${random_id.db_suffix.hex}"
  location_id = var.location_id
  type        = "FIRESTORE_NATIVE"
}