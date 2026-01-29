import boto3
import json
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')
iam = boto3.client('iam')
secretsmanager = boto3.client('secretsmanager')
sns = boto3.client('sns')

def lambda_handler(event, context):
    incident_id = context.request_id
    results = {'incident_id': incident_id, 'isolation': [], 'key_rotation': []}
    
    logger.info(f"Incident Response Started - ID: {incident_id}")
    
    # Handle multiple instances
    instance_ids = event.get('instance_ids', [])
    if 'instance_id' in event:
        instance_ids.append(event['instance_id'])
    
    for instance_id in instance_ids:
        try:
            # Validate instance ID format
            if not instance_id.startswith('i-'):
                raise ValueError(f"Invalid instance ID format: {instance_id}")
            
            vpc_id = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['VpcId']
            
            sg = ec2.create_security_group(
                GroupName=f'isolation-{instance_id}',
                Description='Isolation SG for incident response',
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [
                        {'Key': 'IncidentResponse', 'Value': 'true'},
                        {'Key': 'IncidentId', 'Value': incident_id},
                        {'Key': 'CreatedBy', 'Value': 'SecurityIncidentResponse'}
                    ]
                }]
            )
            sg_id = sg['GroupId']
            
            ec2.revoke_security_group_egress(
                GroupId=sg_id,
                IpPermissions=[{
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }]
            )
            
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=[sg_id]
            )
            
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                DisableApiTermination={'Value': True}
            )
            
            # Tag instance
            ec2.create_tags(
                Resources=[instance_id],
                Tags=[
                    {'Key': 'IncidentResponse', 'Value': 'true'},
                    {'Key': 'IncidentId', 'Value': incident_id},
                    {'Key': 'IsolatedAt', 'Value': datetime.utcnow().isoformat()}
                ]
            )
            
            volumes = ec2.describe_volumes(Filters=[{'Name': 'attachment.instance-id', 'Values': [instance_id]}])
            snapshots = []
            for vol in volumes['Volumes']:
                snap = ec2.create_snapshot(
                    VolumeId=vol['VolumeId'],
                    Description=f'Forensic snapshot - incident {incident_id}',
                    TagSpecifications=[{
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {'Key': 'IncidentResponse', 'Value': 'true'},
                            {'Key': 'IncidentId', 'Value': incident_id}
                        ]
                    }]
                )
                snapshots.append(snap['SnapshotId'])
            
            logger.info(f"Instance isolated: {instance_id}")
            results['isolation'].append({
                'instance_id': instance_id,
                'isolation_sg': sg_id,
                'snapshots': snapshots,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Failed to isolate instance {instance_id}: {str(e)}")
            results['isolation'].append({
                'instance_id': instance_id,
                'status': 'failed',
                'error': 'Isolation failed - check CloudWatch logs'
            })
    
    # Handle multiple IAM users
    compromised_users = event.get('compromised_users', [])
    if 'access_key_id' in event and 'iam_user' in event:
        compromised_users.append({
            'iam_user': event['iam_user'],
            'access_key_id': event['access_key_id']
        })
    
    for user_data in compromised_users:
        try:
            access_key_id = user_data['access_key_id']
            iam_user = user_data['iam_user']
            
            # Validate inputs
            if not access_key_id.startswith('AKIA'):
                raise ValueError(f"Invalid access key format")
            
            iam.update_access_key(
                UserName=iam_user,
                AccessKeyId=access_key_id,
                Status='Inactive'
            )
            
            keys = iam.list_access_keys(UserName=iam_user)['AccessKeyMetadata']
            deleted_keys = []
            
            if len(keys) >= 2:
                inactive_keys = [k for k in keys if k['Status'] == 'Inactive']
                if inactive_keys:
                    oldest = sorted(inactive_keys, key=lambda x: x['CreateDate'])[0]
                    iam.delete_access_key(
                        UserName=iam_user,
                        AccessKeyId=oldest['AccessKeyId']
                    )
                    deleted_keys.append(oldest['AccessKeyId'])
            
            new_key = iam.create_access_key(UserName=iam_user)
            
            secret_name = f"incident-response/{iam_user}/{new_key['AccessKey']['AccessKeyId']}"
            secret_arn = secretsmanager.create_secret(
                Name=secret_name,
                Description=f"Rotated key for {iam_user} - incident {incident_id}",
                SecretString=json.dumps({
                    'AccessKeyId': new_key['AccessKey']['AccessKeyId'],
                    'SecretAccessKey': new_key['AccessKey']['SecretAccessKey'],
                    'UserName': iam_user,
                    'RotatedAt': new_key['AccessKey']['CreateDate'].isoformat(),
                    'IncidentId': incident_id
                }),
                Tags=[
                    {'Key': 'IncidentResponse', 'Value': 'true'},
                    {'Key': 'IncidentId', 'Value': incident_id},
                    {'Key': 'IAMUser', 'Value': iam_user}
                ]
            )['ARN']
            
            logger.info(f"Key rotated for user: {iam_user}")
            results['key_rotation'].append({
                'iam_user': iam_user,
                'deactivated_key': access_key_id,
                'deleted_keys': deleted_keys,
                'new_key_id': new_key['AccessKey']['AccessKeyId'],
                'secret_arn': secret_arn,
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Failed to rotate key for {user_data.get('iam_user')}: {str(e)}")
            results['key_rotation'].append({
                'iam_user': user_data.get('iam_user'),
                'status': 'failed',
                'error': 'Key rotation failed - check CloudWatch logs'
            })
    
    # Send SNS notification
    sns_topic_arn = event.get('sns_topic_arn')
    if sns_topic_arn:
        try:
            sns.publish(
                TopicArn=sns_topic_arn,
                Subject=f'Security Incident Response - {incident_id}',
                Message=json.dumps({
                    'incident_id': incident_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'instances_isolated': len([r for r in results['isolation'] if r['status'] == 'success']),
                    'keys_rotated': len([r for r in results['key_rotation'] if r['status'] == 'success']),
                    'failures': len([r for r in results['isolation'] + results['key_rotation'] if r['status'] == 'failed'])
                }, indent=2)
            )
            logger.info(f"SNS notification sent to {sns_topic_arn}")
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {str(e)}")
    
    logger.info(f"Incident Response Completed - ID: {incident_id}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
