provider "aws" {
  region = "us-east-1"
}

resource "aws_db_instance" "insecure_db" {

  allocated_storage = 20
  engine            = "mysql"
  instance_class    = "db.t3.micro"

  username = "admin"
  password = "password123"

  skip_final_snapshot = true

  storage_encrypted = false
}