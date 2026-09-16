terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_s3_bucket" "evidence" {
  bucket = "grupo4-devsecops-lab-vulnerable"
}

resource "aws_s3_bucket_acl" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  acl    = "public-read"
}

