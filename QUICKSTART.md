# Quick Start Guide

## Package Contents

- `incident_response.py` - Lambda function source code
- `incident_response.zip` - Pre-packaged Lambda deployment file
- `trust-policy.json` - IAM trust policy for Lambda role
- `lambda-policy.json` - IAM permissions policy
- `README.md` - Complete documentation

## Quick Deploy (5 minutes)

### Step 1: Create IAM Role
```bash
# Replace YOUR_ACCOUNT_ID with your AWS account ID
aws iam create-role \
  --role-name IncidentResponseLambdaRole \
  --assume-role-policy-document file://trust-policy.json

aws iam put-role-policy \
  --role-name IncidentResponseLambdaRole \
  --policy-name IncidentResponsePolicy \
  --policy-document file://lambda-policy.json
```

### Step 2: Deploy Lambda
```bash
# Replace YOUR_ACCOUNT_ID with your AWS account ID
aws lambda create-function \
  --function-name SecurityIncidentResponse \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/IncidentResponseLambdaRole \
  --handler incident_response.lambda_handler \
  --timeout 60 \
  --zip-file fileb://incident_response.zip \
  --region us-east-1
```

### Step 3: Test It
```bash
# Create test payload
cat > test-payload.json << EOF
{
  "instance_id": "i-YOUR_INSTANCE_ID",
  "access_key_id": "AKIA_YOUR_KEY",
  "iam_user": "test-user"
}
EOF

# Invoke Lambda
aws lambda invoke \
  --function-name SecurityIncidentResponse \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-payload.json \
  response.json

# Check response
cat response.json
```

## Payload Examples

### Single Resource
```json
{
  "instance_id": "i-0123456789abcdef0",
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "iam_user": "compromised-user"
}
```

### Multiple Resources
```json
{
  "instance_ids": ["i-xxx", "i-yyy"],
  "compromised_users": [
    {"iam_user": "user1", "access_key_id": "AKIA..."},
    {"iam_user": "user2", "access_key_id": "AKIA..."}
  ]
}
```

## What Happens

✅ **EC2 Instances:**
- Isolated with security group (no inbound/outbound traffic)
- Termination protection enabled
- EBS snapshots created

✅ **IAM Users:**
- Compromised keys deactivated
- New keys generated and returned

## Verify in Console

1. **EC2**: https://console.aws.amazon.com/ec2
   - Check instance security groups
   - Verify termination protection
   - View snapshots

2. **IAM**: https://console.aws.amazon.com/iam
   - Check access key status

## Need Help?

See `README.md` for complete documentation.
