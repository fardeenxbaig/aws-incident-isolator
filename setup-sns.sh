#!/bin/bash
# SNS Setup for Security Incident Response

set -e

# Configuration
TOPIC_NAME="SecurityIncidentAlerts"
EMAIL="your-email@company.com"  # Change this!
REGION="us-east-1"

echo "Setting up SNS notifications for Security Incident Response..."

# Create SNS topic
echo "Creating SNS topic: $TOPIC_NAME"
TOPIC_ARN=$(aws sns create-topic \
  --name $TOPIC_NAME \
  --region $REGION \
  --query 'TopicArn' \
  --output text)

echo "Topic ARN: $TOPIC_ARN"

# Subscribe email
echo "Subscribing email: $EMAIL"
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol email \
  --notification-endpoint $EMAIL \
  --region $REGION

echo ""
echo "✅ SNS Setup Complete!"
echo ""
echo "IMPORTANT: Check your email ($EMAIL) and confirm the subscription!"
echo ""
echo "To use with Lambda, add this to your payload:"
echo ""
echo '{
  "instance_ids": ["i-xxx"],
  "compromised_users": [{"iam_user": "user1", "access_key_id": "AKIA..."}],
  "sns_topic_arn": "'$TOPIC_ARN'"
}'
echo ""
echo "Or set as environment variable in Lambda:"
echo "aws lambda update-function-configuration \\"
echo "  --function-name SecurityIncidentResponse \\"
echo "  --environment Variables={SNS_TOPIC_ARN=$TOPIC_ARN} \\"
echo "  --region $REGION"
