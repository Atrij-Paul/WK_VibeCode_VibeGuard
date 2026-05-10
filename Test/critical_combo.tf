provider "aws" {
  region = "us-east-1"
}

# Public SSH Exposure
resource "aws_security_group" "public_ssh" {

  name = "public-ssh"

  ingress {
    description = "SSH open globally"

    from_port   = 22
    to_port     = 22

    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Public S3 Bucket
resource "aws_s3_bucket" "public_bucket" {

  bucket = "critical-company-data"
}

resource "aws_s3_bucket_acl" "public_acl" {

  bucket = aws_s3_bucket.public_bucket.id

  acl = "public-read"
}

# Wildcard IAM Policy
resource "aws_iam_policy" "wildcard_admin" {

  name = "WildcardAdmin"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# Weak Password Policy
resource "aws_iam_account_password_policy" "weak_policy" {

  minimum_password_length = 5

  require_symbols = false
  require_numbers = false
}