#Runscript for Cloudguard Serverless Demo

import boto3
import requests
import getpass
import json
import string
import time
import sys
import urllib.parse
from random import *
from requests.auth import HTTPBasicAuth
from base64 import b64encode
#from nacl import encoding, public


#Prompt User for information
#Dome9
dome9_api_key = input('Dome9 API Key: ')
dome9_api_secret =getpass.getpass('Dome9 Secret Key: ')

#AWS
access_key = input('AWS Access Key: ')
aws_secret_key = getpass.getpass('AWS Secret Key: ')

#Gather Policy Name
read_policy = 'dome9-readonly-policy'
write_policy = 'dome9-write-policy'

#Dome9 API
url = "https://api.dome9.com/v2"



#Menu
print ("Select option: \n")
print("""
        1. Onboard AWS Account and Enable Serverless
        2. Enable Serverless on AWS Account
        """)
selection=input("Select a task number: ")

#Add new AWS account to Dome9
if selection=="1":
    aws_account_name =input('Friendly name of AWS account for Dome9: ')
    
    #Create IAM client for AWS
    iam=boto3.client('iam', aws_access_key_id=access_key,
        aws_secret_access_key=aws_secret_key,)

    #Create IAM Policies

    #Create Dome9 read only policy
    dome9_readonly_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Dome9ReadOnly",
                "Action": [
                    "cloudtrail:LookupEvents",
                    "dynamodb:DescribeTable",
                    "elasticfilesystem:Describe*",
                    "elasticache:ListTagsForResource",
                    "es:ListTags",
                    "firehose:Describe*",
                    "firehose:List*",
                    "guardduty:Get*",
                    "guardduty:List*",
                    "kinesis:List*",
                    "kinesis:Describe*",
                    "kinesisvideo:Describe*",
                    "kinesisvideo:List*",
                    "logs:Describe*",
                    "logs:Get*",
                    "logs:FilterLogEvents",
                    "lambda:List*",
                    "s3:List*",
                    "sns:ListSubscriptions",
                    "sns:ListSubscriptionsByTopic",
                    "sns:ListTagsForResource",
                    "waf-regional:ListResourcesForWebACL",
                    "eks:ListNodegroups",
                    "eks:DescribeNodegroup"
                ],
                "Effect": "Allow",
                "Resource": "*"
            }
        ]
    }

    try:
        response = iam.create_policy(
          PolicyName=read_policy,
          PolicyDocument=json.dumps(dome9_readonly_policy)
        )

    except Exception:
        print ('dome9-readonly-policy already exists!')
        pass

    #Create Dome9 write policy

    dome9_write_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Dome9Write",
                "Action": [
                    "ec2:AuthorizeSecurityGroupEgress",
                    "ec2:AuthorizeSecurityGroupIngress",
                    "ec2:CreateSecurityGroup",
                    "ec2:DeleteSecurityGroup",
                    "ec2:RevokeSecurityGroupEgress",
                    "ec2:RevokeSecurityGroupIngress",
                    "ec2:ModifyNetworkInterfaceAttribute",
                    "ec2:CreateTags",
                    "ec2:DeleteTags"
                ],
                "Effect": "Allow",
                "Resource": "*"
            }
        ]
    }

    try:
        response = iam.create_policy(
          PolicyName=write_policy,
          PolicyDocument=json.dumps(dome9_write_policy)
        )

    except Exception:
        print ('dome9-write-policy already exists! Please select option 2')
        sys.exit()


    #Create Dome9 Role in AWS

    #Generate External ID
    extid = ''.join(choice(string.ascii_letters + string.digits) for _ in range(24))

    #Role Information
    path='/'
    role_name = 'Dome9-Connect'
    description='Dome9 Permissions Role'

    #Trust Policy for Dome9 JSON to variables
    trust_policy={
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "",
          "Effect": "Allow",
          "Principal": {
            "AWS": "arn:aws:iam::634729597623:root"
          },
          "Action": "sts:AssumeRole",
          "Condition": {"StringEquals": {"sts:ExternalId":extid}}
        }
      ]
    }

    tags=[
        {
            'Key': 'Environment',
            'Value': 'Production'
        }
    ]

    #Create Initial Role or update external ID if exists
    try:
        response = iam.create_role(
                Path=path,
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=description,
                MaxSessionDuration=3600,

         )


    except Exception:
        print ('Dome9-Connect role already exists! Please select option 2')
        sys.exit()




    #Add AWS Managed Policies
    aws_policy_list = ['arn:aws:iam::aws:policy/SecurityAudit','arn:aws:iam::aws:policy/AmazonInspectorReadOnlyAccess']

    for arn in aws_policy_list:
        response=iam.attach_role_policy(
            PolicyArn=arn,
            RoleName=role_name
        )                  

    #Get ARN for Dome9 policies

    policy_name_list = [read_policy, write_policy]


    #Parse JSON to grab Arn Prefix

    response = iam.get_role(
        RoleName=role_name
    )


    arn_prefix_tmp = response['Role']['Arn']
    arn_prefix_tmp=arn_prefix_tmp.split(':')
    arn_prefix_tmp=[':'.join(arn_prefix_tmp[0:5])]
    arn_prefix=arn_prefix_tmp[0]



    #Loop through list to Apply Access Policies to the newly created role
    for x in policy_name_list:
        policy_arn = arn_prefix +':policy/'+ x
        response=iam.attach_role_policy(
            PolicyArn=policy_arn,
            RoleName=role_name
        )

    role_arn = arn_prefix+':role/'+role_name


    #Give AWS Time to process commands
    print ("working . . . ")
    time.sleep(20)

    #Attach Account to Dome9
    command = url + "/CloudAccounts"


    json_data = {"name": aws_account_name, "credentials": {"arn":role_arn, "secret": extid, "type": "RoleBased", "isReadOnly": "false"}, "fullProtection": "false", "magellan": "true", "lambdaScanner": "true",
      "serverless": {
        "codeAnalyzerEnabled": "true",
        "codeDependencyAnalyzerEnabled": "true"
      } }

    headers = {'content-type': 'application/json'}

    try: 
        response = requests.post(command, auth=HTTPBasicAuth(dome9_api_key, dome9_api_secret), json=json_data, headers=headers)

        response_json = json.loads(response.content)
        cg_id = response_json['id']
        print ("Added Sucessfully")
        
    except:
        print ("There was a problem adding your account to Dome9.")
        sys.exit()
    
#Option to add to existing account
if selection=="2":
    cg_id = input("Enter Cloudguard ID for AWS Account: ")
 


    
# Enable Serverless Protection on Dome9 (Stage1)
aws_region = "us-east-1" #MUST BE us-east-1 TO RUN. THIS IS WHERE THE S3 EXISTS.
command = url + "/serverless/accounts"

headers = {'content-type': 'application/json'}

json_data = {'cloudAccountId': cg_id}

try: 
    response = requests.post(command, auth=HTTPBasicAuth(dome9_api_key, dome9_api_secret), json=json_data, headers=headers)

    response_json = json.loads(response.content)


    print ("Serverless Protection Stage 1 Complete")
except:
    print ("Error adding Serverless Protection Stage 1")
    sys.exit()


#Enable Serverless AWS (Stage 2)
print ("Starting Stage 2. This will take some time.")
cross_account_url = response_json['crossAccountRoleTemplateURL']
cross_account_template = cross_account_url.split("templateURL=")[1]
template_url = urllib.parse.unquote(cross_account_template)



sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=aws_secret_key,)

response = sts_client.get_caller_identity()
aws_account = response['Account']
stack_name = "ProtegoAccount-Dome9Serverless-" + aws_account


cf_client = boto3.client('cloudformation', region_name=aws_region, aws_access_key_id=access_key, aws_secret_access_key=aws_secret_key,)
cf_client.create_stack(StackName=stack_name, TemplateURL=template_url, Capabilities=["CAPABILITY_NAMED_IAM"])
    
waiter = cf_client.get_waiter('stack_create_complete')
waiter.wait(StackName=stack_name)

print ("Serverless Protection Stage 2 Complete.")

print ("Cloudguard ID: " + cg_id)

print ("Finished!")