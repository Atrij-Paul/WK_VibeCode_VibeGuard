provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "open_ingress_sg" {

  name = "open-ingress"

  ingress {

    from_port   = 0
    to_port     = 65535

    protocol    = "tcp"

    cidr_blocks = ["0.0.0.0/0"]
  }
}