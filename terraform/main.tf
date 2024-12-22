# Create an IoT Thing
resource "aws_iot_thing" "presence_thing" {
  name = "HumanPresenceRadarGateway"
}

# Create an IoT Policy
resource "aws_iot_policy" "thing_policy" {
  name   = "HumanPresenceRadarPolicy"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Subscribe",
        "iot:Connect",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
}

# Create an IoT Certificate
resource "aws_iot_certificate" "thing_certificate" {
  active = true
}

# Attach the Policy to the Certificate
resource "aws_iot_policy_attachment" "policy_attachment" {
  policy = aws_iot_policy.thing_policy.name
  target = aws_iot_certificate.thing_certificate.arn
}

# Attach the Certificate to the Thing
resource "aws_iot_thing_principal_attachment" "thing_principal_attachment" {
  thing     = aws_iot_thing.presence_thing.name
  principal = aws_iot_certificate.thing_certificate.arn
}

# Fetch the IoT Core Data Endpoint
data "aws_iot_endpoint" "iot_endpoint" {
  endpoint_type = "iot:Data-ATS"
}
