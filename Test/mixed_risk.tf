provider "aws" {
  region = "us-east-1"
}

#############################
# SAFE SECURITY GROUP
#############################

resource "aws_security_group" "internal_app_sg" {

  name = "internal-app-sg"

  ingress {

    description = "Internal application traffic"

    from_port   = 8080
    to_port     = 8080

    protocol    = "tcp"

    cidr_blocks = ["10.0.0.0/24"]
  }

  egress {

    from_port   = 0
    to_port     = 0

    protocol    = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }
}

#############################
# DANGEROUS PUBLIC SSH
#############################

resource "aws_security_group" "public_ssh_sg" {

  name = "public-ssh-risk"

  ingress {

    description = "SSH open globally"

    from_port   = 22
    to_port     = 22

    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }
}

#############################
# SAFE PRIVATE S3 BUCKET
#############################

resource "aws_s3_bucket" "private_bucket" {

  bucket = "enterprise-private-data"
}

resource "aws_s3_bucket_acl" "private_acl" {

  bucket = aws_s3_bucket.private_bucket.id

  acl = "private"
}

#############################
# DANGEROUS PUBLIC S3 BUCKET
#############################

resource "aws_s3_bucket" "public_bucket" {

  bucket = "public-sensitive-data"
}

resource "aws_s3_bucket_acl" "public_acl" {

  bucket = aws_s3_bucket.public_bucket.id

  acl = "public-read"
}

#############################
# SAFE IAM POLICY
#############################

resource "aws_iam_policy" "readonly_policy" {

  name = "ReadOnlyPolicy"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]

        Resource = "*"
      }
    ]
  })
}

#############################
# DANGEROUS WILDCARD IAM
#############################

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

#############################
# WEAK PASSWORD POLICY
#############################

resource "aws_iam_account_password_policy" "weak_policy" {

  minimum_password_length = 5

  require_symbols = false
  require_numbers = false

  require_uppercase_characters = false
}

#############################
# SECURE ENCRYPTED DATABASE
#############################

resource "aws_db_instance" "secure_db" {

  allocated_storage = 20

  engine         = "mysql"
  instance_class = "db.t3.micro"

  username = "admin"
  password = "StrongPassword123!"

  storage_encrypted = true

  skip_final_snapshot = true
}

#############################
# INSECURE UNENCRYPTED DATABASE
#############################

resource "aws_db_instance" "insecure_db" {

  allocated_storage = 20

  engine         = "mysql"
  instance_class = "db.t3.micro"

  username = "admin"
  password = "weakpass"

  storage_encrypted = false

  skip_final_snapshot = true
}