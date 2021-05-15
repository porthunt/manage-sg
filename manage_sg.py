import os
import argparse
import boto3
from botocore.exceptions import ClientError
import logging
import sys


logging.basicConfig(
    format="[%(levelname)s] :: %(message)s", level=logging.INFO
)
logger = logging.getLogger("ManageSG")
if os.getenv("DEBUG"):
    sys.tracebacklimit = 0


def create_conn():
    return boto3.client("ec2", region_name=os.getenv("AWS_REGION", "eu-west-2"))


def search_sg(client=None, **kwargs):
    if not kwargs.get("name") and not kwargs.get("description"):
        raise AttributeError("Send either name or description")
    client = create_conn() if not client else client
    sgs = None

    if kwargs.get("name"):
        sgs = client.describe_security_groups(GroupNames=[kwargs.get("name")])

    elif kwargs.get("description"):
        sgs = client.describe_security_groups(
            Filters=[{"Name": "description", "Values": [kwargs.get("description")]}]
        )

    if len(sgs["SecurityGroups"]) != 1:
        raise AttributeError("Multiple SGs found")

    return sgs["SecurityGroups"][0]


def add_ip_to_sg(
    group_id: str,
    ip: str,
    port: int,
    description: str,
    ip_protocol: str = "tcp",
    client=None,
):
    client = create_conn() if not client else client
    try:
        client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    "FromPort": port,
                    "IpProtocol": ip_protocol,
                    "IpRanges": [{"CidrIp": ip, "Description": description}],
                    "ToPort": port,
                }
            ],
        )
    except ClientError as err:
        if "already exists" in str(err):
            logger.error(f"{ip} on port {port} is already allowed")
        raise


def remove_ip_from_sg(
    group_id: str,
    ip: str,
    port: int,
    description: str,
    ip_protocol: str = "tcp",
    client=None,
):
    client = create_conn() if not client else client
    client.revoke_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                "FromPort": port,
                "IpProtocol": ip_protocol,
                "IpRanges": [{"CidrIp": ip, "Description": description}],
                "ToPort": port,
            }
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add IP to Security Group")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--add-ip", help="IP to be added", type=str)
    group.add_argument("--remove-ip", help="IP to be removed", type=str)
    parser.add_argument(
        "--sg-name", help="Name of the security group", type=str
    )
    parser.add_argument("--port", help="Port to allow TCP access", type=int)
    args = parser.parse_args()

    sg_id = search_sg(name=args.sg_name)["GroupId"]

    if args.add_ip:
        logger.info(f"Adding {args.add_ip}:{args.port} to security group '{sg_id}'")
        add_ip_to_sg(
            sg_id, ip=args.add_ip, port=args.port, description="ADDED BY MANAGE_SG"
        )

    elif args.remove_ip:
        logger.info(f"Removing {args.remove_ip}:{args.port} to security group '{sg_id}'")
        remove_ip_from_sg(
            sg_id, ip=args.remove_ip, port=args.port, description="ADDED BY MANAGE_SG"
        )
