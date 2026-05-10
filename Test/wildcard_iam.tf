provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_policy" "admin_policy" {

  name = "FullAdminAccess"

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