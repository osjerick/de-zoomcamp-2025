terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.20.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

resource "google_storage_bucket" "data-lake-bucket" {
  name                        = "taxi-data-${var.common_id}"
  location                    = "US"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    condition {
      age = 7 // days
    }
    action {
      type = "Delete"
    }
  }

  force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = "taxi_data_${replace(var.common_id, "-", "_")}"
  delete_contents_on_destroy = true
}
