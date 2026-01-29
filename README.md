# AWS Incident Isolator | Quarantine Compromised EC2 instances and IAM Access Keys

Automated Lambda function to isolate compromised EC2 instances and rotate leaked IAM access keys.

![Architecture](https://img.shields.io/badge/AWS-Lambda-orange) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Features

- ✅ **EC2 Instance Isolation**: Creates isolation security group with no inbound/outbound rules
- ✅ **Termination Protection**: Enables termination protection on compromised instances
- ✅ **Forensic Snapshots**: Creates EBS volume snapshots for investigation
- ✅ **IAM Key Rotation**: Deactivates compromised keys and creates new ones
- ✅ **Secure Storage**: New credentials stored in AWS Secrets Manager
- ✅ **Bulk Operations**: Handles multiple instances and users in single invocation
- ✅ **SNS Notifications**: Optional real-time alerts to security team
- ✅ **Audit Trail**: Comprehensive CloudWatch logging
- ✅ **Resource Tagging**: All resources tagged for tracking
- ✅ **Error Handling**: Continues processing even if individual resources fail

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Usage](#usage)
- [Security Features](#security-features)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

```
┌─────────────────┐
│  EventBridge    │ (Optional trigger)
│  GuardDuty      │
│  Manual Invoke  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Lambda      │
│   Function      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    ▼         ▼          ▼         ▼
┌───────┐ ┌───────┐ ┌─────────┐ ┌─────┐
│  EC2  │ │  IAM  │ │ Secrets │ │ SNS │
│       │ │       │ │ Manager │ │     │
└───────┘ └───────┘ └─────────┘ └─────┘
```

## 📦 Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.12 runtime
- IAM permissions to create Lambda functions and roles
- AWS account with EC2 and IAM access

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/fardeenxbaig/aws-incident-isolator.git
cd aws-incident-isolator
```

### 2. Deploy Infrastructure
```bash
# Create IAM role
aws iam create-role \
  --role-name IncidentResponseLambdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach permissions
aws iam put-role-policy \
  --role-name IncidentResponseLambdaRole \
  --policy-name IncidentResponsePolicy \
  --policy-document file://lambda-policy.json
```

### 3. Deploy Lambda
```bash
# Replace YOUR_ACCOUNT_ID with your AWS account ID
aws lambda create-function \
  --function-name SecurityIncidentResponse \
  --runtime python3.12 \
  --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/IncidentResponseLambdaRole \
  --handler incident_response.lambda_handler \
  --timeout 60 \
  --zip-file fileb://incident_response.zip \
  --region us-east-1
```

### 4. (Optional) Setup SNS Notifications
```bash
# Edit email in script
nano setup-sns.sh

# Run setup
./setup-sns.sh
```

## 📖 Deployment

See [QUICKSTART.md](QUICKSTART.md) for detailed deployment instructions.

## 🎯 Usage

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
  "instance_ids": [
    "i-0123456789abcdef0",
    "i-0fedcba9876543210"
  ],
  "compromised_users": [
    {
      "iam_user": "user1",
      "access_key_id": "AKIAIOSFODNN7EXAMPLE"
    },
    {
      "iam_user": "user2",
      "access_key_id": "AKIAI44QH8DHBEXAMPLE"
    }
  ]
}
```

### With SNS Notifications
```json
{
  "instance_ids": ["i-xxx"],
  "compromised_users": [{"iam_user": "user1", "access_key_id": "AKIA..."}],
  "sns_topic_arn": "arn:aws:sns:us-east-1:ACCOUNT:SecurityIncidentAlerts"
}
```

### Invoke Lambda
```bash
aws lambda invoke \
  --function-name SecurityIncidentResponse \
  --cli-binary-format raw-in-base64-out \
  --payload file://payload.json \
  response.json
```

## 🔒 Security Features

### What It Does

**EC2 Instance Isolation:**
1. Creates isolation security group (no inbound/outbound traffic)
2. Applies security group to instance
3. Enables termination protection
4. Creates forensic EBS snapshots
5. Tags all resources with incident ID

**IAM Access Key Rotation:**
1. Deactivates compromised key
2. Handles 2-key limit (deletes oldest inactive key if needed)
3. Creates new access key
4. Stores credentials in AWS Secrets Manager (encrypted)
5. Returns secret ARN (not the actual secret)

**Security Enhancements:**
- ✅ Input validation (prevents injection attacks)
- ✅ Structured logging (audit trail without sensitive data)
- ✅ SNS notifications (real-time alerts)
- ✅ Resource tagging (incident tracking)
- ✅ Error handling (no information leakage)

See [SECURITY_ENHANCEMENTS.md](SECURITY_ENHANCEMENTS.md) for complete details.

## 📊 Monitoring

### CloudWatch Logs
```bash
aws logs tail /aws/lambda/SecurityIncidentResponse --follow
```

### Find Incident Resources
```bash
# EC2 instances
aws ec2 describe-instances \
  --filters "Name=tag:IncidentResponse,Values=true"

# Secrets
aws secretsmanager list-secrets \
  --filters Key=tag-key,Values=IncidentResponse

# Snapshots
aws ec2 describe-snapshots \
  --filters "Name=tag:IncidentResponse,Values=true"
```

## 🔧 Troubleshooting

See [README.md](README.md) for detailed troubleshooting guide.

**Common Issues:**
- `InvalidGroup.Duplicate`: Security group already exists - delete it first
- `LimitExceeded`: User has 2 keys - Lambda auto-handles this
- `UnauthorizedOperation`: Lambda role missing permissions

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built for AWS security teams to automate incident response workflows.

## 📞 Support

- Issues: [GitHub Issues](https://github.com/fardeenxbaig/aws-incident-isolator/issues)
- Documentation: See [Quickstart.md](https://github.com/fardeenxbaig/aws-incident-isolator/blob/main/QUICKSTART.md)

## ⚠️ Disclaimer

This tool is provided as-is. Test thoroughly in non-production environments before deploying to production. Always follow your organization's security policies and incident response procedures.
