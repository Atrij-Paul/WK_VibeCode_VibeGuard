provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web_sg" {
  name = "public-ssh-sg"

  ingress {
    description = "SSH access from anywhere"

    from_port   = 22
    to_port     = 22
    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }
}