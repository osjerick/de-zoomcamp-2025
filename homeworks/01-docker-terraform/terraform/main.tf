terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

resource "google_storage_bucket" "data-lake-bucket" {
  name                        = "data-lake-bucket-${var.common_id}"
  location                    = "US"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30 // days
    }
    action {
      type = "Delete"
    }
  }

  force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "data_lake_dataset_${var.common_id}"
}
