#!/usr/bin/env python

"""
Script to create bas service group.
"""

# from troposphere import Base64, FindInMap, GetAtt, Tags
# from troposphere import Parameter, Output, Ref, Template, ImportValue
# from troposphere import Condition, Equals, And, Or, Not, If, Join
# from troposphere.ec2 import SecurityGroup, NetworkInterfaceProperty, Instance, Volume
# from troposphere.ec2 import SecurityGroupRule
import json
import yaml ### for yaml output
from troposphere import Parameter, Template
from troposphere.ec2 import SecurityGroup

t = Template()
###
### parameters
###
#
# vpc_param = t.add_parameter(Parameter(
#     'VPC',
#     ConstraintDescription='must be the VPC Id of an existing VPC.',
#     Description='VPC Id of existing VPC',
#     Type='AWS::EC2::VPC::Id',
#     # Default=Ref(ref_MigrationVPC)
# ))

inrule = t.add_parameter(Parameter(
    'inrule',
    Description='IngressRule',
    Default='[{"CidrIp":"0.0.0.0/0","IpProtocol":"tcp","FromPort":"22","ToPort":"22"}]',
    Type='String'
))
###
### Conditions
###

###
### Resources
###
t.add_resource(SecurityGroup(
    'BaseSecurityGroup',
    GroupDescription='Security group base',
    VpcId='vpc-f5eb1c91',
))
###
### Outputs...
###

# print t.to_json()

### for yaml output...
print yaml.safe_dump(json.loads(t.to_json()), None, allow_unicode=True)
