resource "aws_ecr_repository" "todo_lambda" {
  name                 = "todo-lambda"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
