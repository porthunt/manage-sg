pip install -r requirements.txt > /dev/null
ip_address="$(dig +short myip.opendns.com @resolver1.opendns.com)"
python manage_sg.py --add-ip ${ip_address}/32 --sg-name awseb-e-dzmgkpajs5-stack-AWSEBLoadBalancerSecurityGroup-H1S7N1WWUKT9 --port 80