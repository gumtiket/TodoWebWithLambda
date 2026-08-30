output "ecr_repository_url" {
  value = aws_ecr_repository.todo_lambda.repository_url
}

output "api_invoke_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}
