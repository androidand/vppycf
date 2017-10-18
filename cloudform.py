#!/usr/bin/env python3

# Script for creating a CloudFormation template. By A.S. 2017.

##Resources/docs
# https://github.com/cloudtools/troposphere
# http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/

from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Output, Ref, Template
#import troposphere.ec2 as ec2
from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, Instance, InternetGateway, \
    SecurityGroupRule, SecurityGroup, DHCPOptions
from troposphere.sns import Topic

template = Template()

print("*** Creating CloudFormation template ***")

# Description
template.add_description("Service VPC - used for services")
template.add_metadata([
		{
			"Build":"development", 
			"DependsOn": [],
		    "Environment": "ApiDev",
	        "Revision": "develop",
	        "StackName": "ApiDev-Dev-VPC",
	        "StackType": "InfrastructureResource",
	        "TemplateBucket": "cfn-apidev",
	        "TemplateName": "VPC",
	        "TemplatePath": "ApiDev/Dev/VPC"
        }
	])

# Outputs
template.add_output([
    Output(
        "BastionSG",
        Value=Ref("BastionSG"),
    ),
    Output(
        "CloudWatchAlarmTopic",
        Value=Ref("CloudWatchAlarmTopic"),
    ),
    Output(
        "InternetGateway",
        Value=Ref("InternetGateway"),
    ),
    Output(
        "NatEmergencyTopicARN",
        Value=Ref("NatEmergencyTopic"),
    ),
    Output(
        "VPCID",
        Value=Ref("VPC"),
    ),
    Output(
        "VPCName",
        Value=Ref("AWS::StackName"),
    ),
    Output(
        "VpcNetworkAcl",
        Value=Ref("VpcNetworkAcl"),
    ),
])

# Resources
bastion_sg = SecurityGroup(
	"BastionSG",
	GroupDescription="Used for source/dest rules",
	Tags=[
	{
	"Key": "Environment",
    "Value": "ApiDev"
    },
    {
    "Key": "Name",
    "Value": "ApiDev-Dev-VPC-Bastion-SG"
    },
    {
    "Key": "Owner",
    "Value": "Foo industries"
    },
    {
    "Key": "Service",
    "Value": "ServiceVPC"
    },
    {
    "Key": "VPC",
    "Value": "Dev"
    }],
    VpcId=Ref("VPC")
)
template.add_resource(bastion_sg)

cloud_watch_alarm_topic = Topic(
	"CloudWatchAlarmTopic",
	TopicName="ApiDev-Dev-CloudWatchAlarms"
)
template.add_resource(cloud_watch_alarm_topic)

dhcp_options = DHCPOptions(
	DomainName={Ref("Jaha")},{}
)


# class DHCPOptions(AWSObject):
#     resource_type = "AWS::EC2::DHCPOptions"

#     props = {
#         'DomainName': (basestring, False),
#         'DomainNameServers': (list, False),
#         'NetbiosNameServers': (list, False),
#         'NetbiosNodeType': (integer, False),
#         'NtpServers': (list, False),
#         'Tags': ((Tags, list), False),
#     }






template.add_resource(dhcp_options)

print(template.to_json())