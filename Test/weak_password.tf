provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_account_password_policy" "weak_policy" {

  minimum_password_length = 4

  require_lowercase_characters = false
  require_uppercase_characters = false
  require_numbers              = false
  require_symbols              = false

  allow_users_to_change_password = true
}