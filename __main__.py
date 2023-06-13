import json

import pulumi
from pulumi_aws import cloudwatch, config, ec2, iam, lambda_, route53

from ec2_setup import user_data

###########
# EC2
###########

# Define the AMI ID to use for the EC2 instances
instance_ami = 'ami-0a1622970f82e789c'
instance_type = 't2.medium'

storage_size = 50
# Create a security group for the instances
security_group_http = ec2.SecurityGroup('web-secgrp',
                           description='Enable HTTP and SSH access',
                           ingress=[
                               {
                                   'protocol': 'tcp',
                                   'from_port': 80,
                                   'to_port': 80,
                                   'cidr_blocks': ['0.0.0.0/0'],
                               },
                                {
                                    'protocol': 'tcp',
                                    'from_port': 22,
                                    'to_port': 22,
                                    'cidr_blocks': ['0.0.0.0/0'],
                                },
                           ],
                            egress=[
                                {
                                   'protocol': 'tcp',
                                   'from_port': 443,
                                   'to_port': 443,
                                   'cidr_blocks': ['0.0.0.0/0'],
                                    
                                },
                            ]
                           )


ami_id = pulumi.Output.from_input(instance_ami)


# To view logs run `journalctl -u prefect-agent.service` in a terminal on the EC2


# Specify root block device and add some extra storage
root_block_device = ec2.InstanceRootBlockDeviceArgs(
    volume_size=storage_size,
    volume_type='gp2',
    delete_on_termination=True,
)


# Create an IAM role for the EC2 instance
ec2_role = iam.Role("ec2Role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
        }],
    }),
)

# Create a policy for CloudWatch Logs access
ec2_logs_policy = iam.Policy("ec2LogsPolicy",
    description="A policy to allow EC2 instances to send logs to CloudWatch",
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:logs:*:*:*"
        }],
    }),
)

# Attach the policy to the EC2 role
ec2_logs_policy_attachment = iam.RolePolicyAttachment("ec2LogsPolicyAttachment",
    policy_arn=ec2_logs_policy.arn,
    role=ec2_role.name,
)

# Create an instance profile and associate the role with it
ec2_instance_profile = iam.InstanceProfile("ec2InstanceProfile", role=ec2_role.name)


# Create an EC2 instance
ec2_instance = ec2.Instance("pdm-cc-ec2-instance",
                            instance_type=instance_type,
                            ami=ami_id,
                            vpc_security_group_ids=[security_group_http.id],
                            user_data=user_data,
                            key_name="SUMARAI-EC2",
                            root_block_device=root_block_device,
                            tags={
                                "Name": "PDM-CC: EC2 Streamlit App",
                            },
                            iam_instance_profile=ec2_instance_profile.name,
                            )

###########
# AWS Lambda - General
###########

# Create an IAM role for the Lambda function
# lambda_role = iam.Role("my-lambda-role",
#     assume_role_policy=json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [{
#             "Action": "sts:AssumeRole",
#             "Effect": "Allow",
#             "Principal": {"Service": "lambda.amazonaws.com"},
#         }],
#     }))


# # Create a policy for CloudWatch Logs access
# logs_policy = iam.Policy("logsPolicy",
#     description="A policy to allow Lambda functions to create and write logs to CloudWatch",
#     policy=json.dumps({
#         "Version": "2012-10-17",
#         "Statement": [{
#             "Action": [
#                 "logs:CreateLogGroup",
#                 "logs:CreateLogStream",
#                 "logs:PutLogEvents",
#             ],
#             "Effect": "Allow",
#             "Resource": "arn:aws:logs:*:*:*"
#         }],
#     }),
# )

# # Attach the policy to the Lambda role
# logs_policy_attachment = iam.RolePolicyAttachment("logsPolicyAttachment",
#     policy_arn=logs_policy.arn,
#     role=lambda_role.name,
# )


# # Attach the necessary policy for starting and stopping instances
# iam.RolePolicyAttachment("lambdaRolePolicy",
#     policy_arn="arn:aws:iam::aws:policy/AmazonEC2FullAccess",
#     role=lambda_role.name)

###########
# AWS Lambda - Start
###########

# Create a Lambda function for starting the EC2 instance
# Create the Lambda function for starting the instance
# start_ec2_lambda = lambda_.Function("my-start-lambda",
#     role=lambda_role.arn,
#     runtime="python3.9",
#     handler="start_lambda.start_instance",
#     code=pulumi.AssetArchive({
#         "start_lambda.py": pulumi.FileAsset("start_lambda.py"),
#     }))



# Create EventBridge rules to start and stop the instance every 5 minutes
# start_rule = cloudwatch.EventRule("Start_EC2_Prefect_Worker_Transcription",
#     # schedule_expression="cron(/30 * * * ? *)",
#     schedule_expression="cron(30 10,13 ? * MON-FRI *)",
# )

# start_target = cloudwatch.EventTarget("startInstanceTarget",
#     rule=start_rule.name,
#     arn=start_ec2_lambda.arn,
#     input=ec2_instance.id.apply(lambda id: json.dumps({"instance_id": id})),
# )


# # Add permission for the EventBridge rules to invoke the Lambda functions
# lambda_.Permission("startLambdaPermission",
#     action="lambda:InvokeFunction",
#     function=start_ec2_lambda.name,
#     principal="events.amazonaws.com",
#     source_arn=start_rule.arn)


###########
# AWS Lambda - Stop
###########

# Create Lambda function to stop the EC2 instance
# stop_ec2_lambda = lambda_.Function("stopEc2Instance",
#     role=lambda_role.arn,
#     runtime="python3.8",
#     handler="stop_lambda.stop_instance",
#     code=pulumi.AssetArchive({
#         "stop_lambda.py": pulumi.FileAsset("stop_lambda.py"),
#     }),
#     environment={
#         "variables": {
#             "INSTANCE_ID": ec2_instance.id
#         }
#     }
# )


# # Create an EventBridge rule to stop the instance every 5 minutes, 4 minutes after startup
# stop_rule = cloudwatch.EventRule("Stop_EC2_Prefect_Worker_Transcription",
#     # schedule_expression="cron(20/30 * * * ? *)",
#     schedule_expression="cron(0 11,15 ? * MON-FRI *)",
# )

# stop_target = cloudwatch.EventTarget("StopInstanceTarget",
#     rule=stop_rule.name,
#     arn=stop_ec2_lambda.arn,
# )

# lambda_.Permission("stopLambdaPermission",
#     action="lambda:InvokeFunction",
#     function=stop_ec2_lambda.name,
#     principal="events.amazonaws.com",
#     source_arn=stop_rule.arn)

# # Create an EventBridge rule to stop the instance every 5 minutes, 4 minutes after startup
# stop_rule_debug = cloudwatch.EventRule("Stop_EC2_Prefect_Worker_Transcription_Debug",
#     # schedule_expression="cron(20/30 * * * ? *)",
#     schedule_expression="cron(0 21 * * ? *)",
# )

# stop_target = cloudwatch.EventTarget("StopInstanceTarget_Debug",
#     rule=stop_rule_debug.name,
#     arn=stop_ec2_lambda.arn,
# )

# lambda_.Permission("stopLambdaPermission_Debug",
#     action="lambda:InvokeFunction",
#     function=stop_ec2_lambda.name,
#     principal="events.amazonaws.com",
#     source_arn=stop_rule_debug.arn)


# TODO: purchase a domain via route53, see https://console.aws.amazon.com/route53/
# # Create Elastic IP, to allow SSH connection via a constant IP address

# elastic_ip = ec2.Eip("ElasticIP")

# elastic_ip_association = ec2.EipAssociation("ElasticIPAssociation",
#     instance_id=ec2_instance.id,
#     public_ip=elastic_ip.public_ip
# )


###########
# Stack Output
###########

pulumi.export('ec2_instance_id', ec2_instance.id)
# pulumi.export('elastic_ip_id', elastic_ip.id)
pulumi.export('instance_public_ip', ec2_instance.public_ip)
pulumi.export('instance_public_dns', ec2_instance.public_dns)
# pulumi.export('elastic_ip_public_dns', elastic_ip.public_dns)

# pulumi.export("cloudwatch_logs_url", pulumi.Output.all(region=config.region, instance_id=ec2_instance.id).apply(
#     lambda args: f"https://console.aws.amazon.com/cloudwatch/home?region={args['region']}#logsV2:log-groups/log-group//var/log/messages/log-events/{args['instance_id']}"
# ))


# open template readme and read contents into stack output
with open('./Pulumi.README.md') as f:
    pulumi.export('readme', f.read())
