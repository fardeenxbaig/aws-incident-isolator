# SNS Notification Setup Guide

## Quick Setup (2 minutes)

### Option 1: Using the Script

1. **Edit the script:**
```bash
nano setup-sns.sh
# Change: EMAIL="your-email@company.com"
```

2. **Run the script:**
```bash
./setup-sns.sh
```

3. **Confirm subscription:**
- Check your email inbox
- Click the confirmation link from AWS

4. **Done!** Copy the Topic ARN from the output.

---

### Option 2: Manual Setup

#### Step 1: Create SNS Topic
```bash
aws sns create-topic \
  --name SecurityIncidentAlerts \
  --region us-east-1
```

**Output:**
```json
{
  "TopicArn": "arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts"
}
```

#### Step 2: Subscribe Your Email
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --protocol email \
  --notification-endpoint security-team@company.com \
  --region us-east-1
```

#### Step 3: Confirm Subscription
- Check your email
- Click "Confirm subscription" link

#### Step 4: Verify Subscription
```bash
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts
```

---

## Using SNS with Lambda

### Method 1: Pass in Payload (Recommended)
```json
{
  "instance_ids": ["i-0123456789abcdef0"],
  "compromised_users": [
    {
      "iam_user": "compromised-user",
      "access_key_id": "AKIAIOSFODNN7EXAMPLE"
    }
  ],
  "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts"
}
```

### Method 2: Set as Environment Variable
```bash
aws lambda update-function-configuration \
  --function-name SecurityIncidentResponse \
  --environment Variables={SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts} \
  --region us-east-1
```

Then update Lambda code to read from environment:
```python
sns_topic_arn = event.get('sns_topic_arn') or os.environ.get('SNS_TOPIC_ARN')
```

---

## What You'll Receive

### Email Subject:
```
Security Incident Response - f40a010c-f102-407f-b151-9bc46b322437
```

### Email Body:
```json
{
  "incident_id": "f40a010c-f102-407f-b151-9bc46b322437",
  "timestamp": "2026-01-29T13:20:30Z",
  "instances_isolated": 2,
  "keys_rotated": 2,
  "failures": 0
}
```

---

## Multiple Recipients

### Add Slack/Teams Webhook
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --protocol https \
  --notification-endpoint https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Add SMS
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --protocol sms \
  --notification-endpoint +1234567890
```

### Add Multiple Emails
```bash
# Repeat for each email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --protocol email \
  --notification-endpoint person1@company.com

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --protocol email \
  --notification-endpoint person2@company.com
```

---

## Testing

### Send Test Notification
```bash
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts \
  --subject "Test Alert" \
  --message "This is a test notification"
```

### Test with Lambda
```bash
cat > test-payload.json << EOF
{
  "instance_ids": ["i-test123"],
  "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts"
}
EOF

aws lambda invoke \
  --function-name SecurityIncidentResponse \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-payload.json \
  response.json
```

---

## Troubleshooting

### Not Receiving Emails?

1. **Check spam folder**
2. **Verify subscription status:**
```bash
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts
```
Look for `"SubscriptionArn": "PendingConfirmation"` - means not confirmed yet.

3. **Check Lambda logs:**
```bash
aws logs tail /aws/lambda/SecurityIncidentResponse --follow
```

### Permission Denied?

Add SNS publish permission to Lambda role (already included in `lambda-policy.json`):
```json
{
  "Effect": "Allow",
  "Action": ["sns:Publish"],
  "Resource": "*"
}
```

---

## Cost

- **SNS**: $0.50 per 1 million requests
- **Email**: First 1,000 emails/month free, then $2 per 100,000
- **SMS**: ~$0.00645 per SMS (US)

Typical incident: **< $0.01**

---

## Cleanup

```bash
# Unsubscribe
aws sns unsubscribe --subscription-arn arn:aws:sns:...

# Delete topic
aws sns delete-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:SecurityIncidentAlerts
```
