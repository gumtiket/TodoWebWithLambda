data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "todo_app_lambda" {
  name               = "todo-app-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.todo_app_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "todos_table_access" {
  statement {
    sid    = "TodosTableAccess"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
    ]

    resources = [aws_dynamodb_table.todos.arn]
  }
}

resource "aws_iam_role_policy" "todos_table_access" {
  name   = "todos-table-access"
  role   = aws_iam_role.todo_app_lambda.name
  policy = data.aws_iam_policy_document.todos_table_access.json
}
