pip install -r requirements.txt
apt-get install awscli -y
mkdir ~/.aws
python manage_sg.py --add-ip 143.177.114.119/32 --sg-name awseb-e-dzmgkpajs5-stack-AWSEBLoadBalancerSecurityGroup-H1S7N1WWUKT9 --port 80