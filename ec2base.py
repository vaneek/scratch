#!/usr/bin/env python

"""
Script to create base ec2 instance template.
"""
from troposphere import FindInMap, Tags
from troposphere import Parameter, Ref, Template, ImportValue
from troposphere import If, Join, GetAtt
from troposphere.ec2 import SecurityGroup, NetworkInterfaceProperty, Instance
from troposphere.ec2 import SecurityGroupIngress, SecurityGroupEgress, Volume
from troposphere.iam import Role, InstanceProfile
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole


t = Template()
t.add_description("Template for base ec2 instance.")
t.add_metadata({
    "Comments": "Initial Draft, ec2base",
    "LastUpdated": "28 October 2016",
    "UpdatedBy": "Jeff van Eek",
    "Version": "v1.0",
})

# TODO parameterize subnets and AZs
ref_MigPrivateSubnet = ImportValue("MigPrivateSubnet")
ref_MigPublicSubnet = ImportValue("MigPublicSubnet")
ref_MigPrivateSubnetAZ = GetAtt(ref_MigPrivateSubnet, "AvailabilityZone")
ref_MigPublicSubnetAZ = GetAtt(ref_MigPublicSubnet, "AvailabilityZone")

###
### parameters
###
t.add_parameter(Parameter(
    "Owner",
    Description="Enter Team or Individual Name Responsible for the Stack.",
    Default="tcs",
    Type="String"
))

t.add_parameter(Parameter(
    "Project",
    Description="Enter Project Name.",
    Default="migration",
    Type="String"
))

t.add_parameter(Parameter(
    "DeleteAfter",
    Description="Enter Date It's Ok to Delete the Stack or 'Never' if meant to be persistent.",
    Default="Never",
    Type="String"

))

t.add_parameter(Parameter(
    "Application",
    Description="Application Name",
    Default="application",
    Type="String"
))

t.add_parameter(Parameter(
    "HostName",
    Description="HostName",
    Default="hostname",
    Type="String"
))

keyname_param = t.add_parameter(Parameter(
    "Ec2KeyPair",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Description="Name of an existing EC2 KeyPair to enable SSH/RDP access to \
the instance",
    Type="AWS::EC2::KeyPair::KeyName"
))

vpc_param = t.add_parameter(Parameter(
    "VPC",
    Description="Select VPC.",
    Type="AWS::EC2::VPC::Id"
))

public_param = t.add_parameter(Parameter(
    "AssignPublic",
    Description="Assign Public IP address",
    Type="String",
    Default="false",
    AllowedValues=[
        "true",
        "false"
    ],
    ConstraintDescription="Must be 'true' or 'false'."
))

ostype_param = t.add_parameter(Parameter(
    "OsType",
    Description="Select OS Type of the AMI.",
    Type="String",
    Default="amazon",
    AllowedValues=[
        "amazon",
        "windows",
        "sqlserver"
    ],
    ConstraintDescription="Must be from server list."
))

t.add_parameter(Parameter(
    "InstanceType",
    Type="String",
    Description="EC2 instance type",
    Default="m4.large",
    AllowedValues=[
        "t2.micro", "t2.small", "t2.medium", "t2.large",
        "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge",
        "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge",
        "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge"
    ],
    ConstraintDescription="Must be a valid EC2 instance type.",
))

t.add_parameter(Parameter(
    "BootVolSize",
    Type="String",
    Description="Enter boot volume size in GB, otherwise default for chosen AMI will be used",
    Default=""
))
t.add_parameter(Parameter(
    "Volume2Size",
    Type="String",
    Description="Enter volume size in GB, otherwise empty for none",
    Default=""
))
t.add_parameter(Parameter(
    "Volume3Size",
    Type="String",
    Description="Enter volume size in GB, otherwise empty for none",
    Default=""
))
t.add_parameter(Parameter(
    "Volume4Size",
    Type="String",
    Description="Enter volume size in GB, otherwise empty for none",
    Default=""
))
t.add_parameter(Parameter(
    "Volume5Size",
    Type="String",
    Description="Enter volume size in GB, otherwise empty for none",
    Default=""
))
t.add_parameter(Parameter(
    "Volume6Size",
    Type="String",
    Description="Enter volume size in GB, otherwise empty for none",
    Default=""
))

###
### Mappings
###
### TODO Add custom resource to lookup valid AMI's
### AMI reference (windows,amazon are gp2)
t.add_mapping(
    "AWSRegionOS2AMI", {
        "eu-west-1": {"windows": "ami-55084526", "sqlserver": "ami-1f08456c", \
        "amazon": "ami-d41d58a7"},
        "eu-central-1": {"windows": "ami-0c34ca63", "sqlserver": "ami-7e33cd11", \
        "amazon": "ami-0044b96f"}
    }
)

###
### Conditions
###
# t.add_condition(Condition(
#
# ))
###
### Resources
###
# Attach empty role and profile for future use.
t.add_resource(Role(
    "EC2Role",
    Path="/migration/",
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principal=Principal("Service", ["ec2.amazonaws.com"])
            )
        ]
    )
))
instanceprofile_ec2base = t.add_resource(InstanceProfile(
    "EC2InstanceProfile",
    Path="/migration/",
    Roles=[Ref("EC2Role")]
))

# Base security group to allow instance to access itself.
t.add_resource(SecurityGroup(
    'BaseSecurityGroup',
    GroupDescription='Security group base',
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    )
))
t.add_resource(SecurityGroupIngress(
    'InternalBaseIngress',
    DependsOn="BaseSecurityGroup",
    GroupId=Ref("BaseSecurityGroup"),
    IpProtocol="-1",
    SourceSecurityGroupId=Ref("BaseSecurityGroup")
))
t.add_resource(SecurityGroupEgress(
    'InternalBaseEgress',
    DependsOn="BaseSecurityGroup",
    GroupId=Ref("BaseSecurityGroup"),
    IpProtocol="-1",
    FromPort="0",
    ToPort="65535",
    SourceSecurityGroupId=Ref("BaseSecurityGroup")
))

t.add_resource(Volume(
    'volume2',
    Condition="AddVolume2",
    AvailabilityZone="eu-west-1a",
    Size=Ref("Volume2Size"),
    VolumeType="gp2",
    DeletionPolicy="Snapshot",
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))
t.add_resource(Volume(
    'volume3',
    Condition="AddVolume3",
    AvailabilityZone="eu-west-1a",
    Size=Ref("Volume3Size"),
    VolumeType="gp2",
    DeletionPolicy="Snapshot",
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))
t.add_resource(Volume(
    'volume4',
    Condition="AddVolume4",
    AvailabilityZone="eu-west-1a",
    Size=Ref("Volume4Size"),
    VolumeType="gp2",
    DeletionPolicy="Snapshot",
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))
t.add_resource(Volume(
    'volume5',
    Condition="AddVolume5",
    AvailabilityZone="eu-west-1a",
    Size=Ref("Volume5Size"),
    VolumeType="gp2",
    DeletionPolicy="Snapshot",
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))
t.add_resource(Volume(
    'volume6',
    Condition="AddVolume6",
    AvailabilityZone="eu-west-1a",
    Size=Ref("Volume6Size"),
    VolumeType="gp2",
    DeletionPolicy="Snapshot",
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))

t.add_resource(Instance(
    "ec2server",
    ImageId=FindInMap("AWSRegionOS2AMI", Ref("AWS::Region"), Ref("OsType")),
    InstanceType=Ref("InstanceType"),
    Monitoring="True",
    DisableApiTermination="True",
    KeyName=Ref("Ec2KeyPair"),
    IamInstanceProfile=Ref("EC2InstanceProfile"),
    InstanceInitiatedShutdownBehavior="stop",
    NetworkInterfaces=[
        NetworkInterfaceProperty(
            GroupSet=[
                Ref("BaseSecurityGroup")
            ],
            AssociatePublicIpAddress="false",
            DeviceIndex='0',
            DeleteOnTermination='true',
            # SubnetId=ImportValue("MigPrivateSubnet"),
            SubnetId="subnet-614c5e38",
        )
    ],
    # TODO Add conditional for DeviceName, ie windows or amazon linux.
    BlockDeviceMappings=[
        If(
            "SetBootVolumeSize",
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "VolumeSize": Ref("BootVolSize"),
                    "DeleteOnTermination": "False"
                }
            },
            Ref("AWS::NoValue")
        )
    ],
    Volumes=[
        If("AddVolume2", {"VolumeId": Ref("volume2"), "Device": "xvdb"}, Ref("AWS::NoValue")),
        If("AddVolume3", {"VolumeId": Ref("volume3"), "Device": "xvdc"}, Ref("AWS::NoValue")),
        If("AddVolume4", {"VolumeId": Ref("volume4"), "Device": "xvdd"}, Ref("AWS::NoValue")),
        If("AddVolume5", {"VolumeId": Ref("volume5"), "Device": "xvde"}, Ref("AWS::NoValue")),
        If("AddVolume6", {"VolumeId": Ref("volume6"), "Device": "xvdf"}, Ref("AWS::NoValue"))
    ],
    Tags=Tags(
        Name=Ref("HostName"),
        Application=Join(":", [Ref("Owner"), Ref("Project"), Ref("Application")])
    ),
))


###
### Outputs
###

###
### Metadata
###

###
### Conditions
###
conditions = {
    "SetBootVolumeSize":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "BootVolSize"}, ""]}]
    },
    "AddVolume2":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "Volume2Size"}, ""]}]
    },
    "AddVolume3":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "Volume3Size"}, ""]}]
    },
    "AddVolume4":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "Volume4Size"}, ""]}]
    },
    "AddVolume5":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "Volume5Size"}, ""]}]
    },
    "AddVolume6":{
        "Fn::Not":[{"Fn::Equals":[{"Ref": "Volume6Size"}, ""]}]
    }
}

for k in conditions:
    t.add_condition(k, conditions[k])

print t.to_json()
