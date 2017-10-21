#!/usr/bin/env python3

# Script for creating a CloudFormation template. By A.S. 2017.

##Resources/docs
# https://github.com/cloudtools/troposphere
# http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/

from troposphere import Base64, FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, Instance, InternetGateway, \
    SecurityGroupRule, SecurityGroup, DHCPOptions, VPCDHCPOptionsAssociation, \
    VPCGatewayAttachment
from troposphere.sns import Topic
import argparse
import sys
import helpers as h

template = Template()

#print("*** Creating CloudFormation template ***")

arg = argparse.ArgumentParser()

arg.add_argument(
                "-e",
                "--environment", 
                required=True,
                help="Deployment environment")
arg.add_argument(
                "-w",
                "--write",
                action='store_true',
                help="Write to file. If not specified, output is printed to console.")
args = arg.parse_args()

env = args.environment.capitalize()
environments = ["Test","Dev","Uat","Prod"]
# default = environments[1] # As an alternative to exit we could use default.

#build "development"
#revision "develop"

if env in environments:
    print("Using environment {e}.".format(e=env))
    envl = args.environment.lower()

    
    build = env
    revision = env

else:
    print("Invalid environment, exiting. Please use any of these: {envs}".format(envs=environments))
    sys.exit()


# Description
template.add_description("Service VPC - used for services")
template.add_metadata(
		{
			"Build": h.getBuildAndRevision(env)[0], 
			"DependsOn": [],
		    "Environment": "Api{e}".format(e=env),
	        "Revision": h.getBuildAndRevision(env)[1],
	        "StackName": "Api{e}-{e}-VPC".format(e=env),
	        "StackType": "InfrastructureResource",
	        "TemplateBucket": "cfn-api{el}".format(el=envl),
	        "TemplateName": "VPC",
	        "TemplatePath": "Api{e}/{e}/VPC".format(e=env)
        }
)

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
	Tags=[{
    	"Key": "Environment",
        "Value": "Api{e}".format(e=env)
    },
    {
        "Key": "Name",
        "Value": "Api{e}-{e}-VPC-Bastion-SG".format(e=env)
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
        "Value": env
    }],
    VpcId=Ref("VPC")
)
template.add_resource(bastion_sg)

cloud_watch_alarm_topic = Topic(
	"CloudWatchAlarmTopic",
	TopicName="Api{e}-{e}-CloudWatchAlarms".format(e=env)
)
template.add_resource(cloud_watch_alarm_topic)

dhcp_options = DHCPOptions(
    "DomainName",
    DomainName=Join("",[Ref("AWS::Region"),".compute.internal"]),
    DomainNameServers=["AmazonProvidedDNS"],
    Tags=[{
        "Key": "Environment",
        "Value": "Api{e}".format(e=env)
    },
    {
        "Key": "Name",
        "Value": "Api{e}-{e}-DhcpOptions".format(e=env)
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
        "Value": env
    }]
)
template.add_resource(dhcp_options)

internet_gateway = InternetGateway(
    "InternetGateway",
    Tags=[{
        "Key": "Environment",
        "Value": "Api{e}".format(e=env)
    },
    {
        "Key": "Name",
        "Value": "Api{e}-{e}-InternetGateway".format(e=env)
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
        "Value": env
    }]
)
template.add_resource(internet_gateway)

nat_emergency_topic = Topic(
    "NatEmergencyTopic",
    TopicName="Api{e}-{e}-NatEmergencyTopic".format(e=env)
)
template.add_resource(nat_emergency_topic)

vpc = VPC(
    "VPC",
    CidrBlock="10.0.0.0/16",
    EnableDnsHostnames=True,
    EnableDnsSupport=True,
    InstanceTenancy="default",
    Tags=[{
        "Key": "Environment",
        "Value": "Api{e}".format(e=env)
    },
    {
        "Key": "Name",
        "Value": "Api{e}-{e}-ServiceVPC".format(e=env)
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
        "Value": env
    }]
    )
template.add_resource(vpc)

vpc_dhcp_options_association = VPCDHCPOptionsAssociation(
    "VpcDhcpOptionsAssociation",
    DhcpOptionsId=Ref("DhcpOptions"),
    VpcId=Ref("VPC")
)
template.add_resource(vpc_dhcp_options_association)

vpc_gateway_attachment = VPCGatewayAttachment(
    "VpcGatewayAttachment",
    InternetGatewayId=Ref("InternetGateway"),
    VpcId=Ref("VPC")
)
template.add_resource(vpc_gateway_attachment)

network_acl = NetworkAcl(
    "VpcNetworkAcl",
    Tags=[{
        "Key": "Environment",
        "Value": "Api{e}".format(e=env)
    },
    {
        "Key": "Name",
        "Value": "Api{e}-{e}-NetworkAcl".format(e=env)
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
        "Value": env
    }],
    VpcId=Ref("VPC")
)
template.add_resource(network_acl)

network_in_acl_entry443 = NetworkAclEntry(
    "VpcNetworkAclInboundRulePublic443",
    CidrBlock="0.0.0.0/0",
    Egress=False,
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=PortRange(To="443", From="443"),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=20001
)
template.add_resource(network_in_acl_entry443)

network_in_acl_entry80 = NetworkAclEntry(
    "VpcNetworkAclInboundRulePublic80",
    CidrBlock="0.0.0.0/0",
    Egress=False,
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=PortRange(To="80", From="80"),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=20000
)
template.add_resource(network_in_acl_entry80)

network_out_acl_entry = NetworkAclEntry(
    "VpcNetworkAclOutboundRule",
    CidrBlock="0.0.0.0/0",
    Egress=True,
    NetworkAclId=Ref("VpcNetworkAcl"),
    Protocol="-1",
    RuleAction="allow",
    RuleNumber=30000
)
template.add_resource(network_out_acl_entry)

network_ssh_acl_entry = NetworkAclEntry(
    "VpcNetworkAclSsh",
    CidrBlock="127.0.0.1/32",
    Egress=False,
    NetworkAclId=Ref("VpcNetworkAcl"),
    PortRange=PortRange(To="22", From="22"),
    Protocol="6",
    RuleAction="allow",
    RuleNumber=10000
)
template.add_resource(network_ssh_acl_entry)

template_output = template.to_json()
output_filename = "out-{e}.json".format(e=env)
output_dir = "output/"


if args.write:
    file = open(output_dir + output_filename, "w") 
    file.write(template_output)
    file.close()

else:
    print(template_output)




