resource "aws_apigatewayv2_api" "todo_app" {
  name          = "todo-app"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "todo_app_lambda" {
  api_id                 = aws_apigatewayv2_api.todo_app.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.todo_app.invoke_arn
  payload_format_version = "2.0"
}

locals {
  todo_routes = [
    "GET /todos",
    "POST /todos",
    "GET /todos/{id}",
    "PATCH /todos/{id}",
    "DELETE /todos/{id}",
  ]
}

resource "aws_apigatewayv2_route" "todo_app" {
  for_each  = toset(local.todo_routes)
  api_id    = aws_apigatewayv2_api.todo_app.id
  route_key = each.value
  target    = "integrations/${aws_apigatewayv2_integration.todo_app_lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.todo_app.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.todo_app.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.todo_app.execution_arn}/*/*"
}
