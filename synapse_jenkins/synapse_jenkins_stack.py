from aws_cdk import (Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as r53,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_lambda,
    aws_logs as logs,
    CfnOutput,
    Duration,
    Tags)

import config as config
import aws_cdk.aws_certificatemanager as cm
import aws_cdk.aws_secretsmanager as sm
from constructs import Construct

from aws_cdk.aws_ecr_assets import Platform

ACM_CERT_ARN_CONTEXT = "ACM_CERT_ARN"
IMAGE_PATH_AND_TAG_CONTEXT = "IMAGE_PATH_AND_TAG"
PORT_NUMBER_CONTEXT = "PORT"

# The name of the environment variable that will hold the secrets
SECRETS_MANAGER_ENV_NAME = "SECRETS_MANAGER_SECRETS"
CONTAINER_ENV_NAME = "CONTAINER_ENV"

PRIVATE_KEY_FILE_NAME = "privatekey.pem"
CERTIFICATE_FILE_NAME = "certificate.pem"

BUCKET_NAME = "BUCKET_NAME"

NOTIFICATION_AUTH_SECRET_JSON_KEY="notification_auth"
HTTP_SECRET_SECRET_JSON_KEY="http_secret"

def get_secret(scope: Construct, id: str, name: str) -> str:
    return sm.Secret.from_secret_name_v2(scope, id, name)
    # see also: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ecs/Secret.html
    # see also: ecs.Secret.from_ssm_parameter(ssm.IParameter(parameter_name=name))

def get_container_env(env: dict) -> dict:
    return env.get(CONTAINER_ENV_NAME, {})

def get_bucket_name(env: dict) -> dict:
    return env.get(BUCKET_NAME)

def get_certificate_arn(env: dict) -> str:
    return env.get(ACM_CERT_ARN_CONTEXT)

def get_docker_image_name(env: dict):
    return env.get(IMAGE_PATH_AND_TAG_CONTEXT)

def get_port(env: dict) -> int:
    return int(env.get(PORT_NUMBER_CONTEXT))

class SynapseJenkinsStack(Stack):

    def __init__(self, scope: Construct, context: str, env: dict, vpc: ec2.Vpc, **kwargs) -> None:
        stack_prefix = f'{env.get(config.STACK_NAME_PREFIX_CONTEXT)}'
        stack_id = f'{stack_prefix}-SynapseJenkinsStack'
        super().__init__(scope, stack_id, **kwargs)

 		# Create Security Group
        sec_group = ec2.SecurityGroup(
            self, "MySecurityGroup", vpc=vpc, allow_all_outbound=True
        )
        
        # Create Security Group Ingress Rules
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow SSH access")       
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "allow web access")       
        sec_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8080), "default Jenkins port") # TODO Remove once 443 works       
        
        key_pair_name = "dev-build" # TODO make this a parameter
        
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
        	"exec > /var/log/user-data.log 2>&1",
        	"echo Running user-data script",
        	"sudo dnf update -y && sudo dnf install -y docker",
        	"sudo systemctl enable docker",
        	"sudo systemctl start docker",
        	"sudo docker start jenkins || sudo docker run -d -p 8080:8080 --name jenkins --restart unless-stopped jenkins/jenkins", # TODO specify version
        	"echo User-data script completed successfully"
        	# TODO git clone the source repo'
        	# TODO configure Jenkins
 			# TODO they have a Jenkins pipeline language to define the builds (not sure if it extends to configuring the server).
        )
        
        # Create EC2 instance
        instance = ec2.Instance(
            self,
            "Jenkins",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(), # TODO we want CIS hardened AMI
            vpc=vpc,
            security_group=sec_group,
            associate_public_ip_address=True,
            key_name=key_pair_name,
            user_data=user_data
        )

        # Output Instance ID
        CfnOutput(self, "InstanceId", value=instance.instance_id)

        # Tag all resources in this Stack's scope with context tags
        for key, value in env.get(config.TAGS_CONTEXT).items():
            Tags.of(scope).add(key, value)
