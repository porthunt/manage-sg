import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_ec2
import manage_sg


def create_sg(client):
    response = client.create_security_group(
        Description="Barbaz",
        GroupName="Foobar",
    )
    return response["GroupId"]


def describe_sg(client, sg_id: str):
    response = client.describe_security_groups(GroupIds=[sg_id])
    if len(response["SecurityGroups"]) > 0:
        return response["SecurityGroups"][0]


@mock_ec2
def test_add_ip_to_sg():
    client = boto3.client("ec2", region_name="us-west-1")
    group_id = create_sg(client)
    manage_sg.add_ip_to_sg(
        group_id, ip="0.0.0.0/0", port=1200, description="TEST", client=client
    )
    description = describe_sg(client, sg_id=group_id)
    assert description["GroupName"] == "Foobar"
    assert len(description["IpPermissions"]) == 1
    assert description["IpPermissions"][0]["FromPort"] == 1200
    assert description["IpPermissions"][0]["ToPort"] == 1200
    assert description["IpPermissions"][0]["IpRanges"][0]["CidrIp"] == "0.0.0.0/0"
    assert description["IpPermissions"][0]["IpRanges"][0]["Description"] == "TEST"


@mock_ec2
def test_add_ip_to_sg_nonexistent_sg():
    client = boto3.client("ec2", region_name="us-west-1")
    with pytest.raises(ClientError) as err:
        manage_sg.add_ip_to_sg(
            "sg-xxx", ip="0.0.0.0/0", port=1200, description="TEST", client=client
        )
    assert "does not exist" in str(err)


@mock_ec2
def test_add_ip_to_sg_already_added():
    client = boto3.client("ec2", region_name="us-west-1")
    group_id = create_sg(client)
    manage_sg.add_ip_to_sg(
        group_id, ip="0.0.0.0/0", port=1200, description="TEST", client=client
    )
    with pytest.raises(ClientError) as err:
        manage_sg.add_ip_to_sg(
            group_id, ip="0.0.0.0/0", port=1200, description="TEST", client=client
        )
    assert "The specified rule already exists" in str(err)


@mock_ec2
def test_remove_ip_to_sg():
    client = boto3.client("ec2", region_name="us-west-1")
    group_id = create_sg(client)
    client.authorize_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                "FromPort": 12,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "TEST"}],
                "ToPort": 12,
            }
        ],
    )
    description = describe_sg(client, sg_id=group_id)
    assert description["GroupName"] == "Foobar"
    assert len(description["IpPermissions"]) == 1
    assert description["IpPermissions"][0]["FromPort"] == 12
    assert description["IpPermissions"][0]["ToPort"] == 12
    assert description["IpPermissions"][0]["IpRanges"][0]["CidrIp"] == "0.0.0.0/0"
    assert description["IpPermissions"][0]["IpRanges"][0]["Description"] == "TEST"
    manage_sg.remove_ip_from_sg(
        group_id, ip="0.0.0.0/0", port=12, description="TEST", client=client
    )
    description = describe_sg(client, sg_id=group_id)
    assert description["GroupName"] == "Foobar"
    assert len(description["IpPermissions"]) == 0


@mock_ec2
def test_remove_ip_to_nonexistent_sg():
    client = boto3.client("ec2", region_name="us-west-1")
    with pytest.raises(ClientError) as err:
        manage_sg.remove_ip_from_sg(
            "sg-xxx", ip="0.0.0.0/0", port=1200, description="TEST", client=client
        )
    assert "does not exist" in str(err)


@mock_ec2
def test_search_sg():
    client = boto3.client("ec2", region_name="us-west-1")
    group_id = create_sg(client)
    sg_retrieved = manage_sg.search_sg(client=client, name="Foobar")
    assert group_id == sg_retrieved["GroupId"]


@mock_ec2
def test_search_sg_not_found():
    client = boto3.client("ec2", region_name="us-west-1")
    with pytest.raises(ClientError) as err:
        manage_sg.search_sg(client=client, name="Foobar")
    assert "does not exist" in str(err)
